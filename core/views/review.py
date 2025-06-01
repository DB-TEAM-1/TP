from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.core.paginator import Paginator
from datetime import datetime

def review_list(request):
    with connection.cursor() as cursor:
        # 모든 입양 후기 목록 조회
        cursor.execute("""
            SELECT 
                r.review_id, r.rating, r.comment, r.image_url, r.created_at,
                u.name as user_name,
                a.kindnm, a.popfile1, a.desertionno,
                s.carenm as shelter_name
            FROM review r
            JOIN users u ON r.user_num = u.user_num
            JOIN animal a ON r.desertionno = a.desertionno
            JOIN shelter s ON r.careregno = s.careregno
            ORDER BY r.created_at DESC
        """)
        reviews = dictfetchall(cursor)
        
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
        'current_user': request.session.get('user')
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
        
        if request.method == 'POST':
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            image_url = request.POST.get('image_url', '')  # 선택적 필드
            
            if not rating or not comment:
                messages.error(request, '별점과 후기 내용을 모두 입력해주세요.')
                return redirect('review_create', desertion_no=desertion_no)
            
            # 이미 후기를 작성했는지 확인
            cursor.execute("""
                SELECT review_id
                FROM review
                WHERE user_num = %s AND desertionno = %s
            """, [user_num, desertion_no])
            existing_review = cursor.fetchone()
            
            if existing_review:
                messages.error(request, '이미 후기를 작성하셨습니다.')
                return redirect('review_list')
            
            # 후기 등록
            cursor.execute("""
                INSERT INTO review (
                    user_num, desertionno, careregno, rating, image_url, comment, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, NOW()
                )
            """, [
                user_num,
                desertion_no,
                adoption['careregno'],
                rating,
                image_url,
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
        
        return render(request, 'review/create.html', {'animal': animal})

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
    
    return render(request, 'review/detail.html', {'review': review})

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