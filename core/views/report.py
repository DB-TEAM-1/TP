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
        SELECT *
        FROM report_full_info
        WHERE user_num = %s
        ORDER BY date DESC
    """, [request.session['user']['user_num']])
    
    columns = [col[0] for col in cursor.description]
    reports = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # 디버깅을 위해 각 신고의 image_url 출력
    for report in reports:
        print(f"DEBUG: Report ID: {report.get('report_id')}, Image URL: {report.get('image_url')}")

    # 페이지네이션
    paginator = Paginator(reports, 10)  # 페이지당 10개 항목
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'report/my_list.html', {'reports': page_obj})

def report_list(request):
    """신고 목록 페이지"""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT *
        FROM report_full_info
        ORDER BY date DESC
    """)
    
    reports = dictfetchall(cursor)
    
    # 페이지네이션
    paginator = Paginator(reports, 10)  # 페이지당 10개 항목
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 페이지네이션 블록 계산 (10개씩)
    block_size = 10
    current_block = (page_obj.number - 1) // block_size
    start_page = current_block * block_size + 1
    end_page = start_page + block_size - 1
    
    # 전체 페이지 수를 넘지 않도록 조정
    if end_page > paginator.num_pages:
        end_page = paginator.num_pages
        
    # 표시할 페이지 번호 목록 생성
    page_range = range(start_page, end_page + 1)

    # 이전/다음 블록의 시작 페이지 계산
    prev_block_start_page = None
    if current_block > 0:
        prev_block_start_page = current_block * block_size - block_size + 1

    next_block_start_page = None
    if end_page < paginator.num_pages:
        next_block_start_page = current_block * block_size + block_size + 1
    
    return render(request, 'report/list.html', {
        'reports': page_obj,
        'page_range': page_range, # 현재 블록의 페이지 범위 전달
        'prev_block_start_page': prev_block_start_page, # 이전 블록 시작 페이지 전달
        'next_block_start_page': next_block_start_page, # 다음 블록 시작 페이지 전달
        'show_all_reports': True
    })

def report_create(request):
    # 세션 기반 로그인 체크
    if not request.session.get('user'):
        messages.error(request, '로그인이 필요한 서비스입니다.')
        return redirect('login')

    user_num = request.session['user'].get('user_num')

    # user_num 유효성 확인 (users 테이블에 존재하는지)
    if not user_num:
         messages.error(request, '사용자 정보가 유효하지 않습니다. 다시 로그인해주세요.')
         return redirect('logout') # 유효하지 않은 경우 로그아웃 처리

    with connection.cursor() as cursor:
        cursor.execute("SELECT user_num FROM users WHERE user_num = %s", [user_num])
        user_exists = cursor.fetchone()
        
        if not user_exists:
            messages.error(request, '사용자 정보가 데이터베이스에 없습니다. 다시 로그인해주세요.')
            # 세션 정보가 데이터베이스와 불일치하므로 세션 제거 후 로그아웃
            if 'user' in request.session:
                 del request.session['user']
            return redirect('logout')

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
            # 유효성 검사 실패 시 기존 입력 데이터와 선택지 다시 전달
            context = {
                'form': request.POST,
                'kind_choices': [('개', '개'), ('고양이', '고양이'), ('기타', '기타')],
                'sex_choices': [('M', '수컷'), ('F', '암컷'), ('U', '알 수 없음')],
                'user_num': user_num # user_num 유효성 검사 통과했음을 전달
            }
            # 기존 위치 정보가 있다면 context에 추가 (예: location, caregno)
            if request.POST.get('location'):
                 context['selectedLocation'] = request.POST.get('location')
            if request.POST.get('careregno'):
                 context['selectedShelterId'] = request.POST.get('careregno')

            return render(request, 'report/create.html', context)
        
        # 이미지 처리
        image_path = None
        if image:
            fs = FileSystemStorage()
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.name}"
            image_path = fs.save(f'reports/{filename}', image)
            print(f"DEBUG: Image saved to path: {image_path}") # 저장된 경로 출력

        # 가장 가까운 보호소 찾기 (간단한 구현: 동일 지역 내 첫 번째 보호소)
        # NOTE: 이 부분은 클라이언트에서 선택된 보호소 정보(careregno)를 받아서 사용하는 것이 더 정확합니다.
        # 현재는 location을 기준으로 다시 찾고 있습니다.
        selected_careregno = request.POST.get('careregno')

        if not selected_careregno:
             # location 기반 보호소 찾기 (기존 로직)
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
                     # 유효성 검사 실패 시와 유사하게 context 구성하여 반환
                     context = {
                         'form': request.POST,
                         'kind_choices': [('개', '개'), ('고양이', '고양이'), ('기타', '기타')],
                         'sex_choices': [('M', '수컷'), ('F', '암컷'), ('U', '알 수 없음')],
                         'user_num': user_num
                     }
                     # 기존 위치 정보가 있다면 context에 추가
                     if request.POST.get('location'):
                          context['selectedLocation'] = request.POST.get('location')
                     
                     return render(request, 'report/create.html', context)
                 
                 shelter_id = result[0]
        else:
            # 클라이언트에서 받은 careregno 사용
            shelter_id = selected_careregno


        now = datetime.now()
        
        # 신고 등록
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO report (
                    user_num, careregno, date,
                    location, kindnm, sexcd, image_url,
                    status, description
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                user_num, # 이미 유효성 검사된 user_num 사용
                shelter_id,
                now,  # 날짜와 시간 모두 저장
                location,
                f"{kind} - {breed} ({color})",  # 품종 정보를 하나의 문자열로 결합
                sex,
                image_path, # 파일 시스템에 저장된 상대 경로
                '접수',
                description
            ])
        
        messages.success(request, '신고가 접수되었습니다. 보호소에서 확인 후 연락드리겠습니다.')
        return redirect('home')
    
    # GET 요청: 신고 폼 표시
    # GET 요청 시에도 user_num 유효성 확인
    if not user_num:
         messages.error(request, '사용자 정보가 유효하지 않습니다. 다시 로그인해주세요.')
         return redirect('logout') # 유효하지 않은 경우 로그아웃 처리

    context = {
        'kind_choices': [('개', '개'), ('고양이', '고양이'), ('기타', '기타')],
        'sex_choices': [('M', '수컷'), ('F', '암컷'), ('U', '알 수 없음')],
        'user_num': user_num # 유효성 검사 통과한 user_num 전달 (템플릿에서 활용 가능)
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
        SELECT *
        FROM report_full_info
        WHERE report_id = %s
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