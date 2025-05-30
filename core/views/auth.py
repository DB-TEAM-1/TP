from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
import re

def register(request):
    if request.method == 'POST':
        # 폼 데이터 가져오기
        user_id = request.POST.get('username', '').strip()  # 폼에서는 username으로 받지만 실제로는 id 컬럼에 저장
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        name = request.POST.get('name', '').strip()
        region = request.POST.get('region', '').strip()  # region은 선택사항
        
        # 유효성 검사
        errors = []
        
        # 필수 필드 검사
        if not user_id:
            errors.append('아이디를 입력해주세요.')
        if not email:
            errors.append('이메일을 입력해주세요.')
        if not password:
            errors.append('비밀번호를 입력해주세요.')
        if not password2:
            errors.append('비밀번호 확인을 입력해주세요.')
        if not name:
            errors.append('이름을 입력해주세요.')
        
        # 추가 유효성 검사
        if password and password2 and password != password2:
            errors.append('비밀번호가 일치하지 않습니다.')
        
        if password and len(password) < 8:
            errors.append('비밀번호는 8자 이상이어야 합니다.')
        
        if user_id and not re.match(r'^[a-zA-Z0-9@/./+/-/_]{1,150}$', user_id):
            errors.append('유효하지 않은 아이디 형식입니다.')
        
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('유효하지 않은 이메일 형식입니다.')
        
        # 중복 확인
        if user_id or email:
            with connection.cursor() as cursor:
                if user_id:
                    cursor.execute("SELECT user_num FROM users WHERE id = %s", [user_id])
                    if cursor.fetchone():
                        errors.append('이미 사용 중인 아이디입니다.')
                
                if email:
                    cursor.execute("SELECT user_num FROM users WHERE email = %s", [email])
                    if cursor.fetchone():
                        errors.append('이미 사용 중인 이메일입니다.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'registration/register.html', {
                'form_data': {
                    'username': user_id,
                    'email': email,
                    'name': name,
                    'region': region
                }
            })
        
        # 새로운 user_num 생성
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(user_num) FROM users")
            result = cursor.fetchone()
            max_user_num = result[0] if result[0] is not None else 0
            new_user_num = max_user_num + 1
            
            # 사용자 등록
            cursor.execute("""
                INSERT INTO users (user_num, id, email, password, name, region)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [new_user_num, user_id, email, password, name, region])
            
        # 세션에 사용자 정보 저장
        request.session['user'] = {
            'user_num': new_user_num,
            'id': user_id,
            'name': name,
            'email': email
        }
        messages.success(request, '회원가입이 완료되었습니다.')
        return redirect('home')
    
    return render(request, 'registration/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_num, id, email, name
                FROM users
                WHERE id = %s AND password = %s
            """, [username, password])
            user = dictfetchone(cursor)
        
        if user:
            # 세션에 사용자 정보 저장
            request.session['user'] = user
            messages.success(request, '로그인되었습니다.')
            return redirect('home')
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    
    return render(request, 'registration/login.html')

def logout_view(request):
    # 세션에서 사용자 정보 제거
    if 'user' in request.session:
        del request.session['user']
    messages.success(request, '로그아웃되었습니다.')
    return redirect('home')

def dictfetchone(cursor):
    """Return one row from a cursor as a dict"""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0].lower() for col in cursor.description]
    return dict(zip(columns, row)) 