from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.core.paginator import Paginator
from datetime import datetime
from django.core.files.storage import FileSystemStorage

def review_list(request):
    with connection.cursor() as cursor:
        # 기본 쿼리
        query = """
            SELECT 
                r.review_id, r.rating, r.comment, r.image_url, r.created_at,
                u.name as user_name,
                a.kindnm, a.popfile1, a.desertionno,
                s.carenm as shelter_name
            FROM review r
            JOIN users u ON r.user_num = u.user_num
            JOIN animal a ON r.desertionno = a.desertionno
            JOIN shelter s ON r.careregno = s.careregno
            WHERE 1=1
        """
        params = []
        
        # 필터 적용
        if request.GET.get('shelter'):
            query += " AND s.carenm = %s"
            params.append(request.GET['shelter'])
        
        if request.GET.get('animal'):
            query += " AND a.kindnm = %s"
            params.append(request.GET['animal'])
        
        if request.GET.get('rating'):
            query += " AND r.rating = %s"
            params.append(request.GET['rating'])
        
        if request.GET.get('date'):
            query += " AND DATE(r.created_at) = %s"
            params.append(request.GET['date'])
        
        query += " ORDER BY r.created_at DESC"
        
        cursor.execute(query, params)
        reviews = dictfetchall(cursor)
        
        # 필터 옵션 조회
        cursor.execute("""
            SELECT DISTINCT s.carenm as shelter_name
            FROM review r
            JOIN shelter s ON r.careregno = s.careregno
            ORDER BY s.carenm
        """)
        shelters = [row['shelter_name'] for row in dictfetchall(cursor)]
        
        cursor.execute("""
            SELECT DISTINCT a.kindnm
            FROM review r
            JOIN animal a ON r.desertionno = a.desertionno
            ORDER BY a.kindnm
        """)
        animals = [row['kindnm'] for row in dictfetchall(cursor)]
        
        # 디버깅을 위한 데이터 출력
        print("=== Debug: Review Data ===")
        for review in reviews:
            print(f"Review: {review}")
    
    # 페이지네이션
    paginator = Paginator(reviews, 9)  # 페이지당 9개 항목
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 현재 로그인한 사용자 정보 추가
    context = {
        'reviews': page_obj,
        'is_logged_in': bool(request.session.get('user')),
        'current_user': request.session.get('user'),
        'shelters': shelters,
        'animals': animals,
        'ratings': range(1, 6),  # 1~5 별점
        'selected_shelter': request.GET.get('shelter', ''),
        'selected_animal': request.GET.get('animal', ''),
        'selected_rating': request.GET.get('rating', ''),
        'selected_date': request.GET.get('date', '')
    }
    
    return render(request, 'review/list.html', context)

def review_create(request, desertion_no):
    # 세션 기반 로그인 체크
    if not request.session.get('user'):
        messages.error(request, '로그인이 필요한 서비스입니다.')
        return redirect('login')
    
    user_num = request.session['user']['user_num']
    
    with connection.cursor() as cursor:
        # 해당 동물의 입양이 완료되었는지 확인
        cursor.execute("""
            SELECT a.status, a.careregno
            FROM adoption a
            WHERE a.user_num = %s 
            AND a.desertionno = %s
            AND a.status = '완료됨'
        """, [user_num, desertion_no])
        adoption = dictfetchone(cursor)
        
        if not adoption:
            messages.error(request, '입양이 완료된 동물에 대해서만 후기를 작성할 수 있습니다.')
            return redirect('adoption_list')
        
        # 이미 후기를 작성했는지 확인
        cursor.execute("""
            SELECT review_id, rating, comment, image_url, created_at
            FROM review
            WHERE user_num = %s AND desertionno = %s
        """, [user_num, desertion_no])
        existing_review = dictfetchone(cursor)
        
        if request.method == 'POST':
            if existing_review:
                messages.error(request, '이미 후기를 작성하셨습니다.')
                return redirect('review_list')
            
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            image = request.FILES.get('image_url')  # 파일 업로드로 변경
            
            if not rating or not comment or not image:
                messages.error(request, '별점, 후기 내용, 사진을 모두 입력(첨부)해주세요.')
                return redirect('review_create', desertion_no=desertion_no)
            
            # 이미지 파일 저장
            fs = FileSystemStorage()
            import os
            filename = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.name}"
            image_path = fs.save(f'reviews/{filename}', image)
            
            # 후기 등록
            cursor.execute("""
                INSERT INTO review (
                    user_num, desertionno, careRegNo, rating, image_url, comment, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, NOW()
                )
            """, [
                user_num,
                desertion_no,
                adoption['careregno'],
                rating,
                image_path,
                comment
            ])
            
            messages.success(request, '입양 후기가 등록되었습니다.')
            return redirect('review_list')
        
        # GET 요청: 후기 작성 폼
        cursor.execute("""
            SELECT a.*, s.carenm as shelter_name
            FROM animal a
            JOIN shelter s ON a.careregno = s.careregno
            WHERE a.desertionno = %s
        """, [desertion_no])
        animal = dictfetchone(cursor)
        
        if not animal:
            messages.error(request, '존재하지 않는 동물입니다.')
            return redirect('animal_list')
        
        return render(request, 'review/create.html', {
            'animal': animal,
            'existing_review': existing_review
        })

def review_detail(request, review_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                r.review_id, r.rating, r.comment, r.image_url, r.created_at, r.user_num,
                u.name as user_name,
                a.kindnm, a.popfile1, a.desertionno,
                s.carenm as shelter_name
            FROM review r
            JOIN users u ON r.user_num = u.user_num
            JOIN animal a ON r.desertionno = a.desertionno
            JOIN shelter s ON r.careregno = s.careregno
            WHERE r.review_id = %s
        """, [review_id])
        review = dictfetchone(cursor)
        
        # 디버깅을 위한 데이터 출력
        print("=== Debug: Review Detail ===")
        print(f"Review: {review}")
    
    if not review:
        messages.error(request, '존재하지 않는 후기입니다.')
        return redirect('review_list')
    
    # 현재 로그인한 사용자 정보 추가
    current_user_num = request.session.get('user', {}).get('user_num')

    return render(request, 'review/detail.html', {
        'review': review,
        'current_user_num': current_user_num
    })

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

def review_edit(request, review_id):
    # 세션 기반 로그인 체크
    if not request.session.get('user'):
        messages.error(request, '로그인이 필요한 서비스입니다.')
        return redirect('login')

    user_num = request.session['user']['user_num']

    with connection.cursor() as cursor:
        # 기존 후기 정보 조회
        cursor.execute("""
            SELECT r.*, u.name as user_name, a.kindnm, a.popfile1, a.desertionno
            FROM review r
            JOIN users u ON r.user_num = u.user_num
            JOIN animal a ON r.desertionno = a.desertionno
            WHERE r.review_id = %s
        """, [review_id])
        review = dictfetchone(cursor)

        if not review:
            messages.error(request, '존재하지 않는 후기입니다.')
            return redirect('review_list')

        # 현재 로그인한 사용자가 후기 작성자인지 확인
        if review['user_num'] != user_num:
            messages.error(request, '후기를 수정할 권한이 없습니다.')
            return redirect('review_detail', review_id=review_id)

        if request.method == 'POST':
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            image_url = request.POST.get('image_url', '')

            if not rating or not comment:
                messages.error(request, '별점과 후기 내용을 모두 입력해주세요.')
                return redirect('review_edit', review_id=review_id)

            # 후기 업데이트
            cursor.execute("""
                UPDATE review
                SET rating = %s, comment = %s, image_url = %s
                WHERE review_id = %s
            """, [rating, comment, image_url, review_id])

            messages.success(request, '후기가 성공적으로 수정되었습니다.')
            return redirect('review_detail', review_id=review_id)
        
        return render(request, 'review/edit.html', {'review': review})

def review_delete(request, review_id):
    # 세션 기반 로그인 체크
    if not request.session.get('user'):
        messages.error(request, '로그인이 필요한 서비스입니다.')
        return redirect('login')

    user_num = request.session['user']['user_num']

    with connection.cursor() as cursor:
        # 기존 후기 정보 조회
        cursor.execute("""
            SELECT user_num FROM review WHERE review_id = %s
        """, [review_id])
        review = dictfetchone(cursor)

        if not review:
            messages.error(request, '존재하지 않는 후기입니다.')
            return redirect('review_list')

        # 현재 로그인한 사용자가 후기 작성자인지 확인
        if review['user_num'] != user_num:
            messages.error(request, '후기를 삭제할 권한이 없습니다.')
            return redirect('review_detail', review_id=review_id)

        if request.method == 'POST':
            cursor.execute("DELETE FROM review WHERE review_id = %s", [review_id])
            messages.success(request, '후기가 성공적으로 삭제되었습니다.')
            return redirect('review_list')
        
        messages.error(request, '잘못된 접근입니다.')
        return redirect('review_detail', review_id=review_id) 