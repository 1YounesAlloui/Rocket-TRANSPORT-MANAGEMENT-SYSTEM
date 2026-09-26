from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from livraison.models import Expedition

# Create your views here.


def chauffeur_list(request):
    chauffeurs = Chauffeur.objects.all()
    context = {'chauffeurs' : chauffeurs}
    return render(request, 'fleet/chauffeur_list.html', context)

def vehicules_list(request):
    vehicules = Vehicule.objects.all()
    context = {'vehicules' : vehicules}
    return render(request, 'fleet/vehicule_list.html', context)


def tournee_list(request):
    tournees = Tournee.objects.all().order_by('-date_tournee')
    context = {'tournees': tournees}
    return render(request, 'fleet/tournee_list.html', context)

def chauffeur_create(request):
    if request.method == 'POST':
        form = ChauffeurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('chauffeur_list')
    else:
        form = ChauffeurForm()

    return render(request, 'fleet/chauffeur_form.html', {'form': form})

def vehicule_create(request):
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vehicule_list')
    else:
        form = VehiculeForm()

    return render(request, 'fleet/vehicule_form.html', {'form': form})

def tournee_create(request):
    if request.method == 'POST':
        form = TourneeForm(request.POST)
        if form.is_valid():
            tournee = form.save()

            tournee.chauffeur.disponibilite = False
            tournee.chauffeur.save()

            return redirect('tournee_list')
    else:
        form = TourneeForm()

    return render(request, 'fleet/tournee_form.html', {'form': form})

def incident_create(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tournee_list')
    else:
        form = IncidentForm()

    return render(request, 'fleet/incident_form.html', {'form': form})



def assign_shipments(request, tournee_id):
    tournee = get_object_or_404(Tournee, id=tournee_id)
    expeditions = Expedition.objects.filter(tournee__isnull=True)

    if request.method == 'POST':
        selected_ids = request.POST.getlist('expeditions')

        for exp_id in selected_ids:
            exp = Expedition.objects.get(id=exp_id)
            exp.tournee = tournee
            exp.statut = 'in_transit'
            exp.save()

        return redirect('tournee_list')

    context = {
        'tournee': tournee, 
        'expeditions': expeditions
    }

    return render(request, 'fleet/assign_shipments.html', context)



