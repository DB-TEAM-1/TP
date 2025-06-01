from django.shortcuts import render
from django.db import connection

def home(request):
    with connection.cursor() as cursor:
        # 최근 등록된 동물 조회
        cursor.execute("""
            SELECT a.desertionno, a.kindnm, a.sexcd, a.age, a.location, a.popfile1, a.processstate, s.carenm
            FROM animal a
            JOIN shelter s ON a.careregno = s.careregno
            WHERE a.processstate = '보호중'
            ORDER BY a.date DESC
            LIMIT 6
        """)
        recent_animals = dictfetchall(cursor)
        
        # 디버깅을 위한 출력
        print("Recent animals data:", recent_animals)
        
        # desertionno가 없는 데이터 필터링
        recent_animals = [animal for animal in recent_animals if animal.get('desertionno')]
        
        # 최근 입양 후기 조회
        cursor.execute("""
            SELECT r.*, u.name as user_name
            FROM review r
            JOIN users u ON r.user_num = u.user_num
            ORDER BY r.created_at DESC
            LIMIT 4
        """)
        recent_reviews = dictfetchall(cursor)
        
        # 통계 정보 조회 (수정된 부분)
        # 보호중인 동물 수 조회
        cursor.execute("""
            SELECT COUNT(*) FROM animal WHERE processstate = '보호중'
        """)
        total_animals = cursor.fetchone()[0]

        # 입양 완료 수 조회 (adoption 테이블에서 status가 '완료됨'인 경우)
        cursor.execute("""
            SELECT COUNT(*) FROM adoption WHERE status = '완료됨'
        """)
        total_adoptions = cursor.fetchone()[0]

        # 협력 보호소 수 조회
        cursor.execute("""
            SELECT COUNT(*) FROM shelter
        """)
        total_shelters = cursor.fetchone()[0]

        # 디버깅을 위한 출력
        print("Statistics: total_animals=", total_animals, "total_adoptions=", total_adoptions, "total_shelters=", total_shelters)
    
    context = {
        'recent_animals': recent_animals,
        'recent_reviews': recent_reviews,
        'total_animals': total_animals,
        'total_adoptions': total_adoptions,
        'total_shelters': total_shelters
    }
    
    return render(request, 'home.html', context)

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