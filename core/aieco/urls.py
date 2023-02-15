from django.contrib.auth import views as auth_views
from django.urls import path, include

import aieco.views as views

urlpatterns = [
    #path("accounts/", include("django.contrib.auth.urls")),

    path('', views.IndexView.as_view(), name='Index'),

    path('accounts/singup/', views.SingupView.as_view(), name='Singup'),
    path('accounts/login/',views.UserLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('accounts/email/<uidb64>/<token>/', views.EmailConfirmView, name='email_confirm'),

    path("accounts/password_reset/", views.PasswordResetRequestView, name="password_reset"),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"), name='password_reset_confirm'),    
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'), name='password_reset_complete'),

    path('@', views.ComingSoonView, name='ComingSoon'),

] 
