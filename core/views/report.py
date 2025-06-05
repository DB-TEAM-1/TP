from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.core.files.storage import FileSystemStorage
import os
from datetime import datetime
from django.core.paginator import Paginator

def my_report_list(request):
    """내 신고 목록 페이지"""
    # 로그인 체크
    if 'user' not in request.session:
        return redirect('login')
    
    cursor = connection.cursor()
    cursor.execute("""
        SELECT r.*, u.name as reporter_name, s.carenm as shelter_name
        FROM report r
        LEFT JOIN users u ON r.user_num = u.user_num
        LEFT JOIN shelter s ON r.careregno = s.careregno
        WHERE r.user_num = %s
        ORDER BY r.date DESC
    """, [request.session['user']['user_num']])
    
    columns = [col[0] for col in cursor.description]
    reports = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # 페이지네이션
    paginator = Paginator(reports, 10)  # 페이지당 10개 항목
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'report/my_list.html', {'reports': page_obj})

def report_list(request):
    """신고 목록 페이지"""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT r.*, u.name as reporter_name, s.carenm as shelter_name
        FROM report r
        LEFT JOIN users u ON r.user_num = u.user_num
        LEFT JOIN shelter s ON r.careregno = s.careregno
        ORDER BY r.date DESC
    """)
    
    columns = [col[0] for col in cursor.description]
    reports = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # 페이지네이션
    paginator = Paginator(reports, 10)  # 페이지당 10개 항목
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'report/list.html', {'reports': page_obj})

def report_create(request):
    # 세션 기반 로그인 체크
    if not request.session.get('user'):
        messages.error(request, '로그인이 필요한 서비스입니다.')
        return redirect('login')

    if request.method == 'POST':
        # 폼 데이터 가져오기
        kind = request.POST.get('kind')
        breed = request.POST.get('breed')
        color = request.POST.get('color')
        sex = request.POST.get('sex')
        location = request.POST.get('location')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        # 디버깅을 위한 폼 데이터 출력
        print("받은 폼 데이터:")
        print(f"kind: {kind}")
        print(f"breed: {breed}")
        print(f"color: {color}")
        print(f"sex: {sex}")
        print(f"location: {location}")
        print(f"description: {description}")
        print(f"image: {image}")
        
        # 빈 문자열도 체크하도록 유효성 검사 수정
        missing_fields = []
        if not kind or kind.strip() == '': missing_fields.append('품종')
        if not breed or breed.strip() == '': missing_fields.append('세부 품종')
        if not color or color.strip() == '': missing_fields.append('색상')
        if not sex or sex.strip() == '': missing_fields.append('성별')
        if not location or location.strip() == '': missing_fields.append('발견 장소')
        if not description or description.strip() == '': missing_fields.append('상세 설명')
        if not image: missing_fields.append('사진')
        
        if missing_fields:
            messages.error(request, f'다음 필드를 입력해주세요: {", ".join(missing_fields)}')
            return render(request, 'report/create.html', {
                'form': request.POST,
                'kind_choices': [('개', '개'), ('고양이', '고양이'), ('기타', '기타')],
                'sex_choices': [('M', '수컷'), ('F', '암컷'), ('U', '알 수 없음')]
            })
        
        # 이미지 처리
        image_path = None
        if image:
            fs = FileSystemStorage()
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.name}"
            image_path = fs.save(f'reports/{filename}', image)
        
        # 가장 가까운 보호소 찾기 (간단한 구현: 동일 지역 내 첫 번째 보호소)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT careregno
                FROM shelter
                WHERE careaddr LIKE %s
                LIMIT 1
            """, [f"%{location.split()[0]}%"])  # 첫 번째 지역명으로 검색
            result = cursor.fetchone()
            
            if not result:
                messages.error(request, '해당 지역에 보호소가 없습니다.')
                return render(request, 'report/create.html', {
                    'form': request.POST,
                    'kind_choices': [('개', '개'), ('고양이', '고양이'), ('기타', '기타')],
                    'sex_choices': [('M', '수컷'), ('F', '암컷'), ('U', '알 수 없음')]
                })
            
            shelter_id = result[0]
            now = datetime.now()
            
            # 신고 등록
            cursor.execute("""
                INSERT INTO report (
                    user_num, careregno, date,
                    location, kindnm, sexcd, popfile1,
                    status, description
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                request.session['user']['user_num'],
                shelter_id,
                now.date(),
                location,
                f"{kind} - {breed} ({color})",  # 품종 정보를 하나의 문자열로 결합
                sex,
                image_path,
                '접수',
                description
            ])
        
        messages.success(request, '신고가 접수되었습니다. 보호소에서 확인 후 연락드리겠습니다.')
        return redirect('home')
    
    # GET 요청: 신고 폼 표시
    context = {
        'kind_choices': [('개', '개'), ('고양이', '고양이'), ('기타', '기타')],
        'sex_choices': [('M', '수컷'), ('F', '암컷'), ('U', '알 수 없음')]
    }
    
    return render(request, 'report/create.html', context)

def report_detail(request, report_id):
    """신고 상세 페이지"""
    # 로그인 체크
    if 'user' not in request.session:
        return redirect('login')
    
    # 신고 정보 조회
    cursor = connection.cursor()
    cursor.execute("""
        SELECT r.*, u.name as reporter_name, s.carenm as shelter_name
        FROM report r
        LEFT JOIN users u ON r.user_num = u.user_num
        LEFT JOIN shelter s ON r.careregno = s.careregno
        WHERE r.report_id = %s
    """, [report_id])
    
    columns = [col[0] for col in cursor.description]
    report = dict(zip(columns, cursor.fetchone()))
    
    if not report:
        messages.error(request, '존재하지 않는 신고입니다.')
        return redirect('report_list')
    
    # 신고 작성자만 수정/삭제 가능
    is_owner = request.session['user']['user_num'] == report['user_num']
    
    return render(request, 'report/detail.html', {
        'report': report,
        'is_owner': is_owner
    })

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0].lower() for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ] 