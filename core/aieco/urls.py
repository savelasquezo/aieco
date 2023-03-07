from django.contrib.auth import views as auth_views
from django.urls import path, include

import aieco.views as views

urlpatterns = [
    #path("accounts/", include("django.contrib.auth.urls")),

    path('', views.IndexView.as_view(), name='index'),

    path('accounts/singup/', views.SingupView.as_view(), name='singup'),
    path('accounts/login/',views.iLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='aieco/registration/logout.html'), name='logout'),
    
    path('accounts/email/<uidb64>/<token>/', views.EmailConfirmView, name='email_confirm'),
    path("accounts/password_reset/", views.PasswordResetRequestView, name="password_reset"),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="aieco/registration/password/password_reset_confirm.html"), name='password_reset_confirm'),    
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='aieco/registration/password/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='aieco/registration/password/password_reset_complete.html'), name='password_reset_complete'),


    path('accounts/admin/', views.AccountView.as_view(), name='admin'),
    path('accounts/admin/profile', views.AccountInfoView.as_view(), name='profile'),
    path('accounts/admin/files', views.AccountFilesView.as_view(), name='files'),
    

    path('@', views.ComingSoonView, name='ComingSoon'),

] 
