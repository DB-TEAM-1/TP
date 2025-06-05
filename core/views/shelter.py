from django.shortcuts import render
from django.core.paginator import Paginator
from django.db import connection
from django.http import JsonResponse, Http404

def shelter_list(request):
    """보호소 목록 페이지"""
    cursor = connection.cursor()
    
    # 모든 고유한 도/시 이름 조회
    cursor.execute("""
        SELECT DISTINCT split_part(careaddr, ' ', 1) as province
        FROM shelter
        WHERE careaddr IS NOT NULL AND careaddr != ''
        ORDER BY province
    """)
    all_provinces = [row['province'] for row in dictfetchall(cursor)]
    
    # 지역 데이터 구조화 및 특별자치도 통합
    region_data = {}
    display_provinces = set() # 필터 드롭다운에 표시할 도 목록

    for province in all_provinces:
        # 특별자치도 통합 처리
        if province == '전북특별자치도':
            display_province = '전라북도'
        elif province == '강원특별자치도':
             display_province = '강원도'
        else:
            display_province = province
        
        display_provinces.add(display_province)
        
        # 시/군/구 목록 조회 및 추가
        cursor.execute("""
            SELECT DISTINCT split_part(careaddr, ' ', 2) as city
            FROM shelter
            WHERE split_part(careaddr, ' ', 1) = %s
              AND split_part(careaddr, ' ', 2) IS NOT NULL 
              AND split_part(careaddr, ' ', 2) != ''
            ORDER BY city
        """, [province])
        cities = [row['city'] for row in dictfetchall(cursor)]
        
        if display_province not in region_data:
            region_data[display_province] = []
            
        # 중복 시/군/구 방지 및 추가
        for city in cities:
             if city not in region_data[display_province]:
                 region_data[display_province].append(city)

    # 필터 드롭다운에 표시할 도 목록 정렬
    sorted_display_provinces = sorted(list(display_provinces))

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
    
    selected_province = request.GET.get('province', '')
    selected_city = request.GET.get('city', '')

    if selected_province:
        # '강원도' 또는 '전라북도' 선택 시 특별자치도 포함하여 검색
        if selected_province == '전라북도':
            query += " AND (s.careaddr LIKE %s OR s.careaddr LIKE %s)"
            params.append('전라북도 %')
            params.append('전북특별자치도 %')
        elif selected_province == '강원도':
            query += " AND (s.careaddr LIKE %s OR s.careaddr LIKE %s)"
            params.append('강원도 %')
            params.append('강원특별자치도 %')
        else:
            # 그 외 일반적인 도/시 검색
            query += " AND s.careaddr LIKE %s"
            params.append(f"{selected_province}%")
        
        if selected_city:
             # 시/군/구 필터는 도/시 필터가 적용된 후에만 유효
            if selected_province in ['전라북도', '강원도']:
                 # 전라/강원 특별자치도 포함하여 시/군/구 검색
                 # 기존 도 필터 조건에 추가하여 시/군/구 필터 적용
                 # 예: 전라북도 전주시 -> 전라북도 전주시%, 전북특별자치도 전주시%
                 current_province_condition_index = len(params) - (2 if selected_province in ['전라북도', '강원도'] else 1)
                 current_province_condition = query.split(" AND ")[1 + (1 if request.GET.get('search') else 0) + (1 if request.GET.get('province') else 0) ].strip() # 현재 도 필터 조건 문자열 찾기 - 복잡해지므로 다른 방법 고려 필요

                 # 간소화된 시/군/구 필터링 로직: 선택된 도/특별자치도와 선택된 시를 모두 포함하는 주소 검색
                 city_filter_condition = ""
                 city_params = []
                 
                 city_filter_condition += " AND (s.careaddr LIKE %s"
                 city_params.append(f"{selected_province} {selected_city}%")

                 # 특별자치도 이름으로도 검색 조건 추가
                 if selected_province == '전라북도':
                     city_filter_condition += " OR s.careaddr LIKE %s"
                     city_params.append(f"전북특별자치도 {selected_city}%")
                 elif selected_province == '강원도':
                     city_filter_condition += " OR s.careaddr LIKE %s"
                     city_params.append(f"강원특별자치도 {selected_city}%")

                 city_filter_condition += ")"
                 query += city_filter_condition
                 params.extend(city_params)

            else:
                 # 그 외 일반적인 도/시 검색에 시/군/구 추가
                 query += " AND s.careaddr LIKE %s"
                 params.append(f"{selected_province} {selected_city}%")


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
        'region_data': region_data, # 지역 정보 전달
        'display_provinces': sorted_display_provinces, # 필터 드롭다운에 표시할 도 목록
        'selected_province': selected_province,
        'selected_city': selected_city,
        'search_term': request.GET.get('search', '')
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
        # '강원도' 또는 '전라북도' 검색 시 특별자치도 포함
        if region == '전라북도':
             query += " AND (careaddr LIKE %s OR careaddr LIKE %s)"
             params.append('전라북도 %')
             params.append('전북특별자치도 %')
        elif region == '강원도':
             query += " AND (careaddr LIKE %s OR careaddr LIKE %s)"
             params.append('강원도 %')
             params.append('강원특별자치도 %')
        else:
             query += " AND careaddr LIKE %s"
             params.append(f'{region}%')
    
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