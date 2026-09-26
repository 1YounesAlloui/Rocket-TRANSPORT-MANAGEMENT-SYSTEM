from django.urls import path
from .views import liste_expeditions

urlpatterns = [
    path('expeditions/', liste_expeditions, name='liste_expeditions'),
]