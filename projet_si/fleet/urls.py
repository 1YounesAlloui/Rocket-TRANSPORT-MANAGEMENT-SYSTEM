from django.urls import path
from . import views


urlpatterns = [
    path('chauffeurs/', views.chauffeur_list, name='chauffeur_list'),
    path('chauffeurs/add/', views.chauffeur_create, name='chauffeur_create'),

    path('vehicules/', views.vehicules_list, name='vehicule_list'),
    path('vehicules/add/', views.vehicule_create, name='vehicule_create'),

    path('tournees/', views.tournee_list, name='tournee_list'),
    path('tournees/add/', views.tournee_create, name='tournee_create'),
    path('tournees/<int:tournee_id>/assign/', views.assign_shipments, name='assign_shipments'),

    path('incidents/add/', views.incident_create, name='incident_create'),
]
