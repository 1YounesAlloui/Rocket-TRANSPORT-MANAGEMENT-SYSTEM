from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('expedition/', views.expedition, name='expedition'),
    path('facturation/', views.facturation, name='facturation'),
    path('incidents/', views.incidents, name='incidents'),
    path('reclamation/', views.reclamation, name='reclamation'),
    path('database/', views.database_manager, name='database'),
    path('tournees/', views.tournee_manager, name='tournees'),
    path('tracking/<int:exp_id>/', views.tracking, name='tracking'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]