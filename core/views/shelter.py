from django.shortcuts import render
from django.core.paginator import Paginator
from django.db import connection
from django.http import JsonResponse

def shelter_list(request):
    """보호소 목록 페이지"""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT careregno, carenm, careaddr, caretel
        FROM shelter
        ORDER BY carenm
    """)
    
    columns = [col[0] for col in cursor.description]
    shelters = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # 페이지네이션
    paginator = Paginator(shelters, 10)  # 페이지당 10개 항목
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'shelter/list.html', {'shelters': page_obj})

def shelter_detail(request, shelter_id):
    """보호소 상세 페이지"""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT careregno, carenm, careaddr, caretel
        FROM shelter
        WHERE careregno = %s
    """, [shelter_id])
    
    columns = [col[0] for col in cursor.description]
    shelter = dict(zip(columns, cursor.fetchone()))
    
    return render(request, 'shelter/detail.html', {'shelter': shelter})

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