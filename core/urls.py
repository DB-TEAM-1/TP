from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('animals/search/', views.search_animals, name='search_animals'),
    path('animals/<str:desertionNo>/', views.animal_detail, name='animal_detail'),
    path('shelters/', views.shelter_list, name='shelter_list'),
    path('adoptions/', views.adoption_list, name='adoption_list'),
    path('reviews/<str:careRegNo>/', views.review_list, name='review_list'),
    path('reports/', views.report_list, name='report_list'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
