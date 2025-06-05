from django.shortcuts import render
from django.core.paginator import Paginator
from django.db import connection
from django.http import JsonResponse, Http404

def shelter_list(request):
    """보호소 목록 페이지"""
    cursor = connection.cursor()
    
    # 지역 목록 조회
    cursor.execute("""
        SELECT DISTINCT 
            split_part(careaddr, ' ', 1) as province,
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

    print("Regional Data:", region_data) # 디버그 출력 추가

    # 필터 적용
    params = []
    query = """
        SELECT s.careregno, s.carenm, s.careaddr, s.caretel, 
               s.weekoprstime, s.weekopretime, 
               s.weekendoprstime, s.weekendopretime,
               (SELECT COUNT(*) FROM animal a 
                WHERE a.careregno = s.careregno 
                AND a.processstate = '보호중') as animal_count
        FROM shelter s
        WHERE 1=1
    """
    
    if request.GET.get('province'):
        province = request.GET.get('province')
        # 전라북도와 전북특별자치도, 강원도와 강원특별자치도 예외 처리
        if province == '전라북도':
            query += " AND (s.careaddr LIKE %s OR s.careaddr LIKE %s)"
            params.append('전라북도 %')
            params.append('전북특별자치도 %')
        elif province == '강원도':
            query += " AND (s.careaddr LIKE %s OR s.careaddr LIKE %s)"
            params.append('강원도 %')
            params.append('강원특별자치도 %')
        else:
            query += " AND s.careaddr LIKE %s"
            params.append(f"{province}%")
        
        if request.GET.get('city'):
             # 시/군/구 필터는 도/시 필터가 적용된 후에만 유효
            city = request.GET.get('city')
            # 기존 도/시 필터 조건에 추가하여 시/군/구 필터 적용
            if province in ['전라북도', '강원도']:
                 # 전라/강원 특별자치도 포함하여 시/군/구 검색
                 query += " AND (s.careaddr LIKE %s OR s.careaddr LIKE %s)"
                 params.append(f"{province} {city}%")
                 # 특별자치도 이름으로도 검색
                 if province == '전라북도':
                     params.append(f"전북특별자치도 {city}%")
                 elif province == '강원도':
                     params.append(f"강원특별자치도 {city}%")
            else:
                 # 일반적인 도/시 검색에 시/군/구 추가
                 query += " AND s.careaddr LIKE %s"
                 params.append(f"{province} {city}%")

    if request.GET.get('search'):
        query += " AND (s.carenm LIKE %s OR s.careaddr LIKE %s)"
        search_term = f"%{request.GET['search']}%"
        params.extend([search_term, search_term])
    
    query += " ORDER BY s.carenm"
    
    cursor.execute(query, params)
    shelters = dictfetchall(cursor)

    # 페이지네이션
    paginator = Paginator(shelters, 10)  # 페이지당 10개 항목
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'shelters': page_obj,
        'region_data': region_data # 지역 정보 전달
    }
    
    return render(request, 'shelter/list.html', context)

def shelter_detail(request, shelter_id):
    """보호소 상세 페이지"""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT careregno, carenm, careaddr, caretel,
               weekoprstime, weekopretime, weekendoprstime, weekendopretime
        FROM shelter
        WHERE careregno = %s
    """, [shelter_id])
    
    columns = [col[0] for col in cursor.description]
    shelter = dict(zip(columns, cursor.fetchone()))
    
    # 보호 중인 동물 수 조회 (기존 코드 복원)
    cursor.execute("""
        SELECT COUNT(*) FROM animal 
        WHERE careregno = %s AND processstate = '보호중'
    """, [shelter_id])
    animal_count = cursor.fetchone()[0]
    shelter['animal_count'] = animal_count

    # 보호 중인 동물 목록 조회 (기존 코드 복원)
    cursor.execute("""
        SELECT desertionno, kindcd, kindnm, sexcd, 
               age, weight, happenplace, happendt,
               processstate, popfile1
        FROM animal
        WHERE careregno = %s AND processstate = '보호중'
        ORDER BY happendt DESC
    """, [shelter_id])
    animals = dictfetchall(cursor)
    
    return render(request, 'shelter/detail.html', {
        'shelter': shelter,
        'animals': animals
    })

def shelter_search(request):
    """보호소 검색 API"""
    name = request.GET.get('name', '')
    region = request.GET.get('region', '')
    
    cursor = connection.cursor()
    query = """
        SELECT careregno, carenm, careaddr, caretel
        FROM shelter
        WHERE 1=1
    """
    params = []
    
    if name:
        query += " AND carenm LIKE %s"
        params.append(f'%{name}%')
    
    if region:
        query += " AND careaddr LIKE %s"
        params.append(f'%{region}%')
    
    query += " ORDER BY carenm"
    
    cursor.execute(query, params)
    columns = [col[0] for col in cursor.description]
    shelters = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return JsonResponse(shelters, safe=False)

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