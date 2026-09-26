from django.shortcuts import render
from .models import Expedition

# Create your views here.

def liste_expeditions(request):
    expeditions = Expedition.objects.all()
    return render(request, 'livraison/expeditions.html', {
        'expeditions': expeditions
    })