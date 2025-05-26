from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib import messages
from sql.queries.animal_queries import AnimalQueries
from sql.queries.shelter_queries import ShelterQueries
from sql.queries.adoption_queries import AdoptionQueries
from sql.queries.review_queries import ReviewQueries
from sql.queries.report_queries import ReportQueries
from sql.queries.user_queries import UserQueries

def home(request):
    return render(request, 'core/home.html')

def search_animals(request):
    animals = AnimalQueries.search_animals(
        upKindCd=request.GET.get('upKindCd'),
        sexCd=request.GET.get('sexCd'),
        age=request.GET.get('age'),
        happenPlace=request.GET.get('happenPlace'),
        processState=request.GET.get('processState')
    )
    return JsonResponse({'animals': animals})

def animal_detail(request, desertionNo):
    animal = AnimalQueries.get_animal_detail(desertionNo)
    shelter = AnimalQueries.get_shelter_by_animal(desertionNo)
    return render(request, 'core/animal_detail.html', {
        'animal': animal,
        'shelter': shelter
    })

def shelter_list(request):
    shelters = ShelterQueries.search_shelters(
        region=request.GET.get('region')
    )
    return JsonResponse({'shelters': shelters})

def adoption_list(request):
    if not request.session.get('user_num'):
        return redirect('login')
    adoptions = AdoptionQueries.get_user_adoptions(request.session['user_num'])
    return render(request, 'core/adoption_list.html', {
        'adoptions': adoptions
    })

def review_list(request, careRegNo):
    reviews = ReviewQueries.get_shelter_reviews(careRegNo)
    return render(request, 'core/review_list.html', {
        'reviews': reviews
    })

def report_list(request):
    if not request.session.get('user_num'):
        return redirect('login')
    reports = ReportQueries.get_user_reports(request.session['user_num'])
    return render(request, 'core/report_list.html', {
        'reports': reports
    })

def signup(request):
    if request.method == 'POST':
        try:
            user_num = UserQueries.create_user(
                username=request.POST['username'],
                password=request.POST['password'],
                name=request.POST['name'],
                email=request.POST.get('email'),
                region=request.POST.get('region')
            )
            return redirect('login')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'core/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = UserQueries.get_user_by_username(username)
        
        if user and UserQueries.check_password(password, user['password']):
            request.session['user_num'] = user['user_num']
            request.session['username'] = user['username']
            return redirect('home')
        else:
            messages.error(request, '로그인 정보가 올바르지 않습니다.')
    
    return render(request, 'core/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('home')
