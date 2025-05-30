from django.shortcuts import render
from django.core.paginator import Paginator
from django.db import connection

def shelter_list(request):
    with connection.cursor() as cursor:
        # 기본 쿼리
        query = """
            SELECT s.careregno, s.carenm, s.careaddr, s.caretel, 
                   s.weekoprstime, s.weekopretime, 
                   s.weekendoprstime, s.weekendopretime,
                   s.careregno,
                   (SELECT COUNT(*) FROM animal a 
                    WHERE a.careregno = s.careregno 
                    AND a.processstate = '보호중') as animal_count
            FROM shelter s
            WHERE 1=1
        """
        params = []
        
        # 필터 적용
        if request.GET.get('region'):
            query += " AND careaddr LIKE %s"
            params.append(f"%{request.GET['region']}%")
        
        if request.GET.get('search'):
            query += " AND (carenm LIKE %s OR careaddr LIKE %s)"
            search_term = f"%{request.GET['search']}%"
            params.extend([search_term, search_term])
        
        query += " ORDER BY carenm"
        
        cursor.execute(query, params)
        shelters = dictfetchall(cursor)
        
        # 지역 목록 조회 - PostgreSQL 버전
        cursor.execute("""
            SELECT DISTINCT 
                split_part(careaddr, ' ', 1) || ' ' || split_part(careaddr, ' ', 2) AS region
            FROM shelter
            ORDER BY region
        """)
        regions = [row['region'] for row in dictfetchall(cursor)]

    
    # 페이지네이션
    paginator = Paginator(shelters, 10)  # 페이지당 10개 항목
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'shelters': page_obj,
        'regions': regions
    }
    
    return render(request, 'shelter/list.html', context)

def shelter_detail(request, shelter_id):
    with connection.cursor() as cursor:
        # 보호소 정보 조회
        cursor.execute("""
            SELECT s.careregno, s.carenm, s.careaddr, s.caretel, 
                   s.weekoprstime, s.weekopretime, 
                   s.weekendoprstime, s.weekendopretime,
                   s.careregno,
                   (SELECT COUNT(*) FROM animal a 
                    WHERE a.careregno = s.careregno 
                    AND a.processstate = '보호중') as animal_count
            FROM shelter s
            WHERE s.careregno = %s
        """, [shelter_id])
        shelter = dictfetchone(cursor)
        
        if not shelter:
            raise Http404("Shelter not found")
        
        # 보호 중인 동물 목록 조회
        cursor.execute("""
            SELECT a.desertionno, a.kindcd, a.kindnm, a.sexcd, 
                   a.age, a.weight, a.happenplace, a.happendt,
                   a.processstate, a.popfile1
            FROM animal a
            WHERE a.careregno = %s AND a.processstate = '보호중'
            ORDER BY a.happendt DESC
        """, [shelter['careregno']])
        animals = dictfetchall(cursor)
    
    context = {
        'shelter': shelter,
        'animals': animals
    }
    
    return render(request, 'shelter/detail.html', context)

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def dictfetchone(cursor):
    """Return one row from a cursor as a dict"""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row)) 