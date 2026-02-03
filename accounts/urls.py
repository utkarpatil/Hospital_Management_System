"""
URL Configuration for Accounts App
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    
    # User management endpoints
    path('me/', views.current_user, name='current-user'),
    path('update/', views.update_user, name='update-user'),
    path('change-password/', views.change_password, name='change-password'),
]