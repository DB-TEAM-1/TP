from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('animals/', views.animals, name='animals'),
    path('shelters/', views.shelters, name='shelters'),
    path('reports/', views.reports, name='reports'),
    path('adoptions/', views.adoptions, name='adoptions'),
    path('reviews/', views.reviews, name='reviews'),

    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
