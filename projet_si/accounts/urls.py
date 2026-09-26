from django.urls import path
from . import views


urlpatterns = [
    path('signin/', views.signin, name='signin'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_stats, name='dashboard'),
    path('factures/', views.liste_factures, name='liste_factures'),
    path('factures/payer/<int:facture_id>/', views.enregistrer_paiement, name='enregistrer_paiement'),
]
