from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.core.files.storage import FileSystemStorage
import os
from datetime import datetime

def report_list(request):
    # 세션 기반 로그인 체크
    if not request.session.get('user'):
        messages.error(request, '로그인이 필요한 서비스입니다.')
        return redirect('login')
    
    with connection.cursor() as cursor:
        # 현재 로그인한 사용자의 신고 목록 조회
        cursor.execute("""
            SELECT r.report_id, r.reported_dt, r.reported_time, 
                   r.location, r.estimated_kind, r.status,
                   s.carenm, s.caretel
            FROM report r
            JOIN shelter s ON r.careregno = s.careregno
            WHERE r.user_num = %s
            ORDER BY r.reported_dt DESC, r.reported_time DESC
        """, [request.session['user']['user_num']])
        my_reports = dictfetchall(cursor)
        
        # 전체 신고 목록 조회 (최근 10개)
        cursor.execute("""
            SELECT r.report_id, r.reported_dt, r.reported_time, 
                   r.location, r.estimated_kind, r.status,
                   s.carenm, u.name as reporter_name
            FROM report r
            JOIN shelter s ON r.careregno = s.careregno
            JOIN users u ON r.user_num = u.user_num
            ORDER BY r.reported_dt DESC, r.reported_time DESC
            LIMIT 10
        """)
        recent_reports = dictfetchall(cursor)
    
    context = {
        'my_reports': my_reports,
        'recent_reports': recent_reports
    }
    
    return render(request, 'report/list.html', context)

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
                    user_num, careregno, reported_dt, reported_time,
                    location, estimated_kind, sex_cd, image_url,
                    status, description
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                request.session['user']['user_num'],
                shelter_id,
                now.date(),
                now.time(),
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

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0].lower() for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ] 