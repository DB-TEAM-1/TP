from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Animal
from .models import Shelter
from .forms import CustomUserCreationForm

def home(request):
    return render(request, 'core/home.html')

def animals(request):
    animals = Animal.objects.all().order_by('-happenDt')[:30]  # 최근 30건 출력
    return render(request, 'core/animals.html', {'animals': animals})

def shelters(request):
    shelters = Shelter.objects.all().order_by('careNm')
    return render(request, 'core/shelters.html', {'shelters': shelters})

def reports(request):
    return render(request, 'core/reports.html')

def adoptions(request):
    return render(request, 'core/adoptions.html')

def reviews(request):
    return render(request, 'core/reviews.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/signup.html', {'form': form})
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '로그인 정보가 올바르지 않습니다.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')
