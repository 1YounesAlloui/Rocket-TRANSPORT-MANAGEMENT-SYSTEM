from datetime import datetime, timedelta
from django.db import transaction
import json
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.contrib import messages
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from decimal import Decimal
from fleet.models import Tournee, Incident, Chauffeur, Vehicule
from livraison.models import Expedition, Destination, TypeService, Tarification, SuiviExpedition
from accounts.models import Client, Reclamation, Facture, Paiement, Utilisateur






def index(request):
    """Landing page / Welcome screen"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'Rocket/index.html')

@login_required
def dashboard(request):
    user = request.user
    context = {}

    # --- FIXED HELPER: Uses correct date fields per model ---
    def get_evolution(model, date_field, sum_field=None):
        today = timezone.now()
        this_month = today.month
        last_month = 12 if this_month == 1 else this_month - 1
        
        # Dynamic filter keys based on the model's date field
        curr_filter = {f"{date_field}__month": this_month}
        prev_filter = {f"{date_field}__month": last_month}

        curr_qs = model.objects.filter(**curr_filter)
        prev_qs = model.objects.filter(**prev_filter)

        curr_val = curr_qs.aggregate(s=Sum(sum_field))['s'] if sum_field else curr_qs.count()
        prev_val = prev_qs.aggregate(s=Sum(sum_field))['s'] if sum_field else prev_qs.count()
        
        curr_val, prev_val = (curr_val or 0), (prev_val or 0)
        if prev_val == 0: return "+0"
        
        percent = ((curr_val - prev_val) / prev_val) * 100
        return f"{'+' if percent >= 0 else ''}{round(percent, 1)}"

    # --- ADMIN / RESPONSIBLE LOGIC ---
    if user.is_staff or getattr(user, 'role', None) == 'ADMIN':
        
        # 1. Commercial Analysis (Uses 'date_creation')
        context['evolution_expeditions'] = get_evolution(Expedition, 'date_creation')
        context['evolution_revenue'] = get_evolution(Expedition, 'date_creation', 'montant_total')
        context['total_expeditions'] = Expedition.objects.count()
        context['total_revenue'] = Expedition.objects.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        
        context['top_clients'] = Client.objects.annotate(
            total_spent=Sum('expedition__montant_total')).order_by('-total_spent')[:5]
        
        # Top 5 Destinations les plus sollicitées
        context['top_destinations'] = Destination.objects.annotate(
            nb_expeditions=Count('expedition')).order_by('-nb_expeditions')[:5]
        
        top_dest = context['top_destinations'].first() if context['top_destinations'] else None
        context['top_destination'] = top_dest.ville if top_dest else "N/A"

        # 2. Operational Analysis (Uses 'date_tournee' for Tournee)
        context['evolution_tours'] = get_evolution(Tournee, 'date_tournee')
        context['total_tours'] = Tournee.objects.count()

        # Taux de réussite des livraisons (détaillé)
        total_exps = context['total_expeditions']
        livrees = Expedition.objects.filter(statut='Livré').count()
        echecs = Expedition.objects.filter(statut='Échec').count()
        en_cours = total_exps - livrees - echecs
        
        context['deliveries'] = {
            'livrees': livrees,
            'echecs': echecs,
            'en_cours': en_cours,
            'taux_reussite': round((livrees / total_exps * 100), 1) if total_exps > 0 else 0,
            'taux_echec': round((echecs / total_exps * 100), 1) if total_exps > 0 else 0
        }
        context['success_rate'] = context['deliveries']['taux_reussite']

        context['top_chauffeurs'] = Chauffeur.objects.annotate(
            nb_tours=Count('tournee')).order_by('-nb_tours')[:5]

        # Zones géographiques avec le plus d'incidents
        context['zones_incidents'] = Destination.objects.annotate(
            nb_incidents=Count('expedition__reclamation')).order_by('-nb_incidents')[:5]
        
        crit_zone = context['zones_incidents'].first() if context['zones_incidents'] else None
        context['critical_zone'] = crit_zone.ville if crit_zone else "Aucune"

        # Peak Period (12-month window)
        peak = Expedition.objects.annotate(month=TruncMonth('date_creation')).values('month').annotate(
            count=Count('id')).order_by('-count').first()
        context['peak_period'] = peak['month'].strftime('%B %Y') if peak else "N/A"
        
        context['recent_activity'] = Expedition.objects.select_related('client').order_by('-date_creation')[:5]

    # --- CLIENT / CHAUFFEUR LOGIC ---
    elif getattr(user, 'role', None) == 'CLIENT':
        client = Client.objects.filter(email=user.email).first()
        if client:
            context['client_stats'] = {
                'total_shipments': Expedition.objects.filter(client=client).count(),
                'solde': client.solde,
                'active_claims': Reclamation.objects.filter(client=client).exclude(statut='RESOLU').count()
            }

    elif getattr(user, 'role', None) == 'CHAUFFEUR':
        driver = Chauffeur.objects.filter(nom=user.last_name).first()
        if driver:
            context['driver_stats'] = {
                'total_tours': Tournee.objects.filter(chauffeur=driver).count(),
                'last_tour': Tournee.objects.filter(chauffeur=driver).order_by('-date_tournee').first(),
                'incident_count': Reclamation.objects.filter(tournee__chauffeur=driver).count()
            }

    return render(request, 'Rocket/dashboard.html', context)


@login_required
def expedition(request):
    if request.method == 'POST':
        p = request.POST

        if 'delete_expedition_id' in p:
            Expedition.objects.filter(id=p.get('delete_expedition_id')).delete()
            return redirect('expedition')
            
        try:
            # 1. Retrieve IDs from the form
            dest_id = p.get('destination')
            client_id = p.get('client')
            service_id = p.get('type_service')
            
            # Validation: Prevent crash if user didn't select something
            if not all([dest_id, client_id, service_id]):
                messages.error(request, "Veuillez remplir tous les champs obligatoires.")
                return redirect('expedition')

            # 2. Get Database Objects
            dest = get_object_or_404(Destination, id=dest_id)
            client = get_object_or_404(Client, id=client_id)
            srv = get_object_or_404(TypeService, id=service_id)

            # 3. Apply Formula
            poids = float(p.get('poids') or 0)
            volume = float(p.get('volume') or 0)
            
            # Use the Expedition.save() logic for calculation if needed, 
            # but here we can keep the view logic for specificity or let the model handle it.
            # Let's let the model handle it by passing montant_total=None or 0
            
            # 4. Create the record in the Database
            exp = Expedition.objects.create(
                numero_expedition=p.get('numero_expedition') or None,
                client=client,
                destination=dest,
                type_service=srv,
                poids=poids,
                volume=volume,
                description=p.get('description'),
                statut='Enregistré'
            )
            
            # 5. Add to Journal (Tracking History)
            SuiviExpedition.objects.create(
                expedition=exp,
                lieu="Entrepôt Rocket",
                statut_etape="Enregistré",
                commentaire="L'expédition a été enregistrée dans le système."
            )

            messages.success(request, f"Expédition {exp.numero_expedition} enregistrée avec succès!")
            
        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement : {e}")
            
        return redirect('expedition')

    # --- GET LOGIC ---
    # Ensure standard service types exist for selection
    for lib in ["Standard", "Express", "International"]:
        TypeService.objects.get_or_create(libelle=lib)

    tarifs_dict = {}
    for t in Tarification.objects.select_related('destination', 'type_service').all():
        key = f"{t.destination.id}_{t.type_service.id}"
        tarifs_dict[key] = {
            "base": float(t.tarif_base),
            "poids": float(t.tarif_poids),
            "volume": float(t.tarif_volume)
        }
        
    return render(request, 'Rocket/expedition.html', {
        'expeditions': Expedition.objects.all().order_by('-date_creation'),
        'destinations': Destination.objects.all(),
        'clients': Client.objects.all(),
        'services': TypeService.objects.all(),
        'tarifs_json': json.dumps(tarifs_dict)
    })


@login_required
def facturation(request):
    if request.method == 'POST':
        p = request.POST
        
        # --- LOGIQUE DE SUPPRESSION ---
        if 'delete_facture_id' in p:
            f = get_object_or_404(Facture, id=p.get('delete_facture_id'))
            # On récupère le total payé pour cette facture avant de la supprimer
            total_paye = Paiement.objects.filter(facture=f).aggregate(Sum('montant'))['montant__sum'] or 0
            # On retire la dette impayée du solde client
            f.client.solde -= (f.montant_TTC - Decimal(str(total_paye)))
            f.client.save()
            f.delete()
        
        # --- LOGIQUE DE CRÉATION ---
        elif 'client_id' in p:
            client = get_object_or_404(Client, id=p.get('client_id'))
            exp_ids = p.getlist('expeditions')
            exps = Expedition.objects.filter(id__in=exp_ids)
            
            # Calculs financiers
            ht = Decimal(p.get('montant_ht') or 0)
            tva = ht * Decimal('0.19')  # TVA 19%
            ttc = ht + tva
            
            paid_val = p.get('montant_paye', '0').replace(',', '.')
            paid = Decimal(paid_val) if paid_val else Decimal('0')
            
            # Création de la facture
            statut = 'PAYEE' if paid >= ttc else 'PARTIEL' if paid > 0 else 'IMPAYEE'
            facture = Facture.objects.create(
                client=client,
                montant_HT=ht,
                montant_TVA=tva,
                montant_TTC=ttc,
                statut=statut
            )
            
            # Lier les expéditions à la facture
            facture.expeditions.set(exps)
            
            # Enregistrer le paiement
            if paid > 0:
                Paiement.objects.create(
                    facture=facture,
                    montant=paid,
                    mode_paiement=p.get('mode_paiement', 'Espèces')
                )
            
            # Mise à jour automatique du solde client
            client.solde += (ttc - paid)
            client.save()
            
        return redirect('facturation')

    # --- LOGIQUE DE CONSULTATION (GET) ---
    factures = Facture.objects.all().order_by('-date_facture')
    
    # Calculer MV et MR pour chaque facture
    for facture in factures:
        # Montant Versé = somme de tous les paiements pour cette facture
        total_paye = Paiement.objects.filter(facture=facture).aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
        facture.montant_verse = total_paye
        # Montant Restant = TTC - MV
        facture.montant_restant = facture.montant_TTC - total_paye
    
    context = {
        'factures': factures,
        'clients': Client.objects.all(),
        'uninvoiced_expeditions': Expedition.objects.filter(facture__isnull=True),
        'paiements': Paiement.objects.all().order_by('-date_paiement')[:10]
    }
    return render(request, 'Rocket/facturation.html', context)

@login_required
def incidents(request):
    p = request.POST
    if request.method == 'POST':
        if 'delete_incident_id' in p:
            Incident.objects.filter(id=p.get('delete_incident_id')).delete()
        else:
            inc = Incident.objects.create(
                type_incident=p.get('type_incident'), description=p.get('description'),
                date_incident=p.get('date_incident'), gravite=p.get('gravite'),
                expedition_id=p.get('expedition_id') or None, tournee_id=p.get('tournee_id') or None,
                preuve=request.FILES.get('preuve')
            )
            if inc.expedition:
                inc.expedition.statut = 'Échec'
                inc.expedition.save()
        return redirect('incidents')

    return render(request, 'Rocket/incidents.html', {
        'incidents': Incident.objects.order_by('-date_incident'),
        'expeditions': Expedition.objects.all(),
        'tournees': Tournee.objects.all(),
        'type_choices': Incident.TYPE_CHOICES,
        'gravite_choices': Incident.GRAVITE_CHOICES
    })


@login_required
def reclamation(request):
    p = request.POST
    if request.method == 'POST':
        if 'resolve_id' in p:
            rec = get_object_or_404(Reclamation, id=p.get('resolve_id'))
            rec.statut = 'RESOLUE'
            rec.save()
        else:
            rec = Reclamation.objects.create(
                client_id=p.get('client_id'), objet=p.get('objet'), commentaire=p.get('commentaire'),
                facture_id=p.get('facture_id') or None, assigned_to_id=p.get('assigned_to_id') or None
            )
            if p.getlist('expeditions'):
                rec.expeditions.set(Expedition.objects.filter(id__in=p.getlist('expeditions')))
        return redirect('reclamation')

    return render(request, 'Rocket/reclamation.html', {
        'reclamations': Reclamation.objects.order_by('-date'),
        'clients': Client.objects.all(),
        'expeditions': Expedition.objects.all(),
        'factures': Facture.objects.all(),
        'agents': Utilisateur.objects.filter(is_staff=True),
        'active_reclamations': Reclamation.objects.filter(statut='EN_COURS').count()
    })

@login_required
def database_manager(request):
    if not (request.user.is_staff or getattr(request.user, 'role', None) == 'ADMIN'):
        return redirect('dashboard')

    if request.method == 'POST':
        p = request.POST
        a = p.get('action')
        
        if a == 'add_client':
            Client.objects.create(nom=p.get('nom'), prenom=p.get('prenom'), email=p.get('email'), telephone=p.get('telephone'), adresse=p.get('adresse'))
        elif a == 'del_client':
            Client.objects.filter(id=p.get('id')).delete()
        elif a == 'add_chauffeur':
            Chauffeur.objects.create(nom=p.get('nom'), prenom=p.get('prenom'), permis=p.get('permis'), telephone=p.get('telephone'), date_embauche=p.get('date_embauche'))
        elif a == 'del_chauffeur':
            Chauffeur.objects.filter(id=p.get('id')).delete()
        elif a == 'add_vehicule':
            Vehicule.objects.create(immatriculation=p.get('immatriculation'), type=p.get('type'), capacite=p.get('capacite'), etat=p.get('etat'))
        elif a == 'del_vehicule':
            Vehicule.objects.filter(id=p.get('id')).delete()
        elif a == 'add_destination':
            Destination.objects.create(ville=p.get('ville'), pays=p.get('pays'), zone_geographique=p.get('zone'), tarif_base=p.get('tarif_base'), tarif_poids=p.get('tarif_poids'), tarif_volume=p.get('tarif_volume'))
        elif a == 'del_destination':
            Destination.objects.filter(id=p.get('id')).delete()
        
        return redirect('database')

    context = {
        'clients': Client.objects.all(),
        'chauffeurs': Chauffeur.objects.all(),
        'vehicules': Vehicule.objects.all(),
        'destinations': Destination.objects.all()
    }
    return render(request, 'Rocket/database.html', context)

@login_required
def tournee_manager(request):
    p = request.POST
    if request.method == 'POST':
        a = p.get('action')
        if a == 'create_tour':
            t = Tournee.objects.create(date_tournee=p.get('date_tournee'), chauffeur_id=p.get('chauffeur_id'), vehicule_id=p.get('vehicule_id'))
            exps = Expedition.objects.filter(id__in=p.getlist('expeditions'))
            t.expeditions.set(exps)
            for e in exps:
                e.statut = 'En livraison'
                e.save()
                SuiviExpedition.objects.create(expedition=e, lieu="Entrepôt", statut_etape="Chargement", commentaire=f"Assigné à la tournée #{t.id}")
        elif a == 'update_tour_data':
            t = get_object_or_404(Tournee, id=p.get('tour_id'))
            t.kilometrage, t.consommation_carburant = p.get('km'), p.get('carburant')
            t.save()
        return redirect('tournees')

    return render(request, 'Rocket/tournees.html', {
        'tournees': Tournee.objects.order_by('-date_tournee'),
        'chauffeurs': Chauffeur.objects.filter(disponibilite=True),
        'vehicules': Vehicule.objects.all(),
        'available_expeditions': Expedition.objects.filter(statut='Enregistré')
    })

@login_required
def tracking(request, exp_id):
    e = get_object_or_404(Expedition, id=exp_id)
    if request.method == 'POST':
        p = request.POST
        SuiviExpedition.objects.create(expedition=e, lieu=p.get('lieu'), statut_etape=p.get('statut'), commentaire=p.get('commentaire'))
        e.statut = p.get('statut')
        e.save()
        return redirect('tracking', exp_id=exp_id)

    return render(request, 'Rocket/tracking.html', {'expedition': e, 'status_choices': Expedition.STATUT_CHOICES})


