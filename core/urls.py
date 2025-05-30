from django.urls import path
from .views import home, animal, shelter, report, auth

urlpatterns = [
    # 메인 페이지
    path('', home.home, name='home'),
    
    # 동물 관련
    path('animals/', animal.animal_list, name='animal_list'),
    path('animals/<str:desertion_no>/', animal.animal_detail, name='animal_detail'),
    path('animals/<str:desertion_no>/adopt/', animal.adoption_apply, name='adoption_apply'),
    
    # 보호소 관련
    path('shelters/', shelter.shelter_list, name='shelter_list'),
    path('shelters/<int:shelter_id>/', shelter.shelter_detail, name='shelter_detail'),
    
    # 신고 관련
    path('reports/', report.report_list, name='report_list'),
    path('reports/create/', report.report_create, name='report_create'),
    
    # 인증 관련
    path('register/', auth.register, name='register'),
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),
    
    # 입양 신청 관련 URL
    path('adoption/', animal.adoption_list, name='adoption_list'),
    path('adoption/apply/<str:desertion_no>/', animal.adoption_apply, name='adoption_apply'),
]
