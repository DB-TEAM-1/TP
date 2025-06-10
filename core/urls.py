from django.urls import path
from .views import home, animal, shelter, report, auth, review

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
    path('api/shelters/search/', shelter.shelter_search, name='shelter_search'),
    
    # 신고 관련
    path('reports/create/', report.report_create, name='report_create'),
    path('reports/list/', report.report_list, name='report_list'),
    path('reports/my-list/', report.my_report_list, name='my_report_list'),
    path('reports/<int:report_id>/', report.report_detail, name='report_detail'),
    
    # 인증 관련
    path('register/', auth.register, name='register'),
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),
    
    # 입양 신청 관련
    path('adoption/', animal.adoption_list, name='adoption_list'),
    path('adoption/apply/<str:desertion_no>/', animal.adoption_apply, name='adoption_apply'),
    
    # 입양 후기 관련
    path('reviews/', review.review_list, name='review_list'),
    path('reviews/create/<str:desertion_no>/', review.review_create, name='review_create'),
    path('reviews/<int:review_id>/', review.review_detail, name='review_detail'),
    path('reviews/<int:review_id>/edit/', review.review_edit, name='review_edit'),
    path('reviews/<int:review_id>/delete/', review.review_delete, name='review_delete'),
]
