from django.urls import path
from . import views

urlpatterns = [
    path('', views.Account, name='account'),         
    path('login/', views.Login, name='login'),      
    path('register/', views.Register, name='register'), 
    path('logout/', views.Logout, name='logout'),
]