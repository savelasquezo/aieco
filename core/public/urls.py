from django.contrib.auth import views as auth_views
from django.urls import path, include

import public.views as views

urlpatterns = [
    #path("accounts/", include("django.contrib.auth.urls")),

    path('', views.IndexView.as_view(), name='index'),
    path('legal/<str:iURL>', views.LegalView.as_view(), name='legal'),
    path('about-us', views.AboutUsView.as_view(), name='about-us'),

    path('accounts/singup', views.SingupView.as_view(), name='singup'),
    path('accounts/login',views.iLoginView.as_view(), name='login'),
    path('accounts/logout', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    
    path("accounts/password_reset", views.PasswordResetRequestView, name="password_reset"),
    path('accounts/reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password/password_reset_confirm.html"), name='password_reset_confirm'),    
    path('accounts/password_reset/done', auth_views.PasswordResetDoneView.as_view(template_name='registration/password/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/done', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password/password_reset_complete.html'), name='password_reset_complete'),


    path('accounts/admin', views.AccountView.as_view(), name='admin'),
    path('accounts/admin/files', views.AccountFilesView.as_view(), name='files'),
    path('accounts/admin/galery', views.AccountGaleryView.as_view(), name='galery'),
    path('accounts/admin/support', views.AccountSupportView.as_view(), name='support'),

    path('accounts/admin/billing', views.AccountBillingView.as_view(), name='billing'),
    path('accounts/admin/billing/pdf', views.MakePDFView.as_view(), name='invoice'),
    path('accounts/admin/billing/history', views.AccountHistoryView.as_view(), name='history'),

    path('@', views.ComingSoonView, name='ComingSoon'),

] 
