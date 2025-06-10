from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib import messages
from datetime import datetime

def animal_list(request):
    with connection.cursor() as cursor:
        # 기본 쿼리
        query = """
            SELECT a.desertionno, a.kindcd, a.kindnm, a.sexcd, a.age, 
                   a.location, a.popfile1, a.processstate, a.date,
                   s.carenm, s.careaddr, s.caretel
            FROM animal a
            JOIN shelter s ON a.careregno = s.careregno
            WHERE a.processstate = '보호중'
        """
        params = []
        
        # 필터 적용
        filters = []
        if request.GET.get('kind'):
            filters.append("a.kindcd = %s")
            params.append(request.GET['kind'])
        if request.GET.get('sex'):
            filters.append("a.sexcd = %s")
            params.append(request.GET['sex'])
        if request.GET.get('shelter'):
            filters.append("s.careregno = %s")
            params.append(request.GET['shelter'])
        if request.GET.get('province'):
            province = request.GET.get('province')
            if request.GET.get('city'):
                filters.append("s.careaddr LIKE %s")
                params.append(f"{province} {request.GET['city']}%")
            else:
                # 전라북도와 강원도 선택 시 특별자치도 데이터도 포함
                if province == '전라북도':
                    filters.append("(s.careaddr LIKE %s OR s.careaddr LIKE %s)")
                    params.extend(['전라북도%', '전북특별자치도%'])
                elif province == '강원도':
                    filters.append("(s.careaddr LIKE %s OR s.careaddr LIKE %s)")
                    params.extend(['강원도%', '강원특별자치도%'])
                else:
                    filters.append("s.careaddr LIKE %s")
                    params.append(f"{province}%")
        
        if filters:
            query += " AND " + " AND ".join(filters)
        
        query += " ORDER BY a.date DESC"
        
        cursor.execute(query, params)
        animals = dictfetchall(cursor)
        
        # 디버깅을 위해 데이터 출력
        print("=== Debug: Animal Data ===")
        for animal in animals:
            print(f"Animal: {animal}")
        
        # desertionno가 없는 데이터 필터링
        animals = [animal for animal in animals if animal.get('desertionno') is not None]  # PostgreSQL은 소문자로 반환할 수 있음
        
        # 필터링 후 데이터 확인
        print("=== After Filtering ===")
        print(f"Remaining animals: {len(animals)}")
        
        # 품종 목록 조회
        cursor.execute("""
            SELECT DISTINCT kindcd, kindnm
            FROM animal
            ORDER BY kindnm
        """)
        kinds = dictfetchall(cursor)
        
        # 지역 목록 조회
        cursor.execute("""
            SELECT DISTINCT 
                CASE 
                    WHEN split_part(careaddr, ' ', 1) = '전북특별자치도' THEN '전라북도'
                    WHEN split_part(careaddr, ' ', 1) = '강원특별자치도' THEN '강원도'
                    ELSE split_part(careaddr, ' ', 1)
                END as province,
                split_part(careaddr, ' ', 2) as city
            FROM shelter
            ORDER BY province, city
        """)
        regions = dictfetchall(cursor)
        
        # 지역 데이터 구조화
        region_data = {}
        for region in regions:
            province = region['province']
            city = region['city']
            if province not in region_data:
                region_data[province] = []
            if city:  # city가 비어있지 않은 경우에만 추가
                region_data[province].append(city)
    
    # 페이지네이션
    paginator = Paginator(animals, 12)  # 페이지당 12개 항목
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'animals': page_obj,
        'kinds': kinds,
        'region_data': region_data
    }
    
    return render(request, 'animal/list.html', context)

def animal_detail(request, desertion_no):
    with connection.cursor() as cursor:
        # 동물 정보 조회
        cursor.execute("""
            SELECT a.desertionno, a.kindcd, a.kindnm, a.sexcd, a.age,
                   a.location, a.popfile1, a.processstate, a.date,
                   a.neuteryn, a.weight, a.specialmark,
                   s.carenm, s.careaddr, s.caretel, s.careregno,
                   s.weekoprstime, s.weekopretime,
                   s.weekendoprstime, s.weekendopretime
            FROM animal a
            JOIN shelter s ON a.careregno = s.careregno
            WHERE a.desertionno = %s
        """, [desertion_no])
        result = dictfetchone(cursor)
        
        if not result:
            raise Http404("Animal not found")
        
        # 입양 후기 조회
        cursor.execute("""
            SELECT r.*, u.name as user_name
            FROM review r
            JOIN users u ON r.user_num = u.user_num
            WHERE r.desertionno = %s
            ORDER BY r.created_at DESC
        """, [desertion_no])
        reviews = dictfetchall(cursor)
    
    # 현재 URL 쿼리 파라미터 확인
    is_from_adoption_list = request.GET.get('from') == 'adoption'
    
    context = {
        'animal': result,
        'shelter': result,  # 보호소 정보도 포함되어 있음
        'reviews': reviews,
        'is_from_adoption_list': is_from_adoption_list  # 입양 신청 현황에서 접근했는지 여부
    }
    
    return render(request, 'animal/detail.html', context)

def adoption_list(request):
    # 세션 기반 로그인 체크
    if not request.session.get('user'):
        messages.error(request, '로그인이 필요한 서비스입니다.')
        return redirect('login')
    
    user_num = request.session['user']['user_num']

    with connection.cursor() as cursor:
        # 현재 로그인한 사용자의 입양 신청 목록 조회
        cursor.execute("""
            SELECT a.adoption_id, a.applied_at, a.status,
                   an.desertionno, an.kindnm, an.sexcd, an.age,
                   s.carenm, s.caretel
            FROM adoption a
            JOIN animal an ON a.desertionno = an.desertionno
            JOIN shelter s ON a.careregno = s.careregno
            WHERE a.user_num = %s
            ORDER BY a.applied_at DESC
        """, [user_num])
        adoptions = dictfetchall(cursor)

        # 각 입양 건에 대해 후기 작성 여부 확인
        for adoption in adoptions:
            cursor.execute("""
                SELECT review_id FROM review
                WHERE user_num = %s AND desertionno = %s
            """, [user_num, adoption['desertionno']])
            existing_review = cursor.fetchone()
            if existing_review:
                adoption['has_review'] = True
                adoption['review_id'] = existing_review[0] # review_id 추가
            else:
                adoption['has_review'] = False
                adoption['review_id'] = None
    
    return render(request, 'animal/adoption_list.html', {'adoptions': adoptions})

def adoption_apply(request, desertion_no):
    # 세션 기반 로그인 체크
    if not request.session.get('user'):
        messages.error(request, '로그인이 필요한 서비스입니다.')
        return redirect('login')

    user_num = request.session['user']['user_num']

    with connection.cursor() as cursor:
        # 사용자 존재 여부 확인
        cursor.execute("""
            SELECT user_num FROM users WHERE user_num = %s
        """, [user_num])
        user = cursor.fetchone()
        
        if not user:
            messages.error(request, '사용자 정보가 올바르지 않습니다. 다시 로그인해주세요.')
            return redirect('logout')  # 로그아웃 처리

        # 이미 신청한 동물인지 확인
        cursor.execute("""
            SELECT status
            FROM adoption
            WHERE user_num = %s AND desertionno = %s
            AND status NOT IN ('거절됨')
        """, [user_num, desertion_no])
        existing_adoption = cursor.fetchone()
        
        if existing_adoption:
            messages.error(request, '이미 입양 신청한 동물입니다.')
            return redirect('animal_detail', desertion_no=desertion_no)
        
        # 동물과 보호소 정보 조회
        cursor.execute("""
            SELECT a.*, s.careregno
            FROM animal a
            JOIN shelter s ON a.careregno = s.careregno
            WHERE a.desertionno = %s
        """, [desertion_no])
        animal = dictfetchone(cursor)
        
        if not animal:
            messages.error(request, '존재하지 않는 동물입니다.')
            return redirect('animal_list')
        
        if animal['processstate'] != '보호중':
            messages.error(request, '현재 입양 신청이 불가능한 동물입니다.')
            return redirect('animal_detail', desertion_no=desertion_no)
        
        # 입양 신청 등록
        cursor.execute("""
            INSERT INTO adoption (
                user_num, desertionno, careregno, applied_at, status
            ) VALUES (
                %s, %s, %s, NOW(), '신청'
            )
        """, [
            user_num,
            desertion_no,
            animal['careregno']
        ])
    
    messages.success(request, '입양 신청이 완료되었습니다. 보호소에서 검토 후 연락드리겠습니다.')
    return redirect('adoption_list')

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0].lower() for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def dictfetchone(cursor):
    """Return one row from a cursor as a dict"""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0].lower() for col in cursor.description]
    return dict(zip(columns, row)) 