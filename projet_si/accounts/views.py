from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count
from .models import Facture, Paiement, Client, Reclamation, Utilisateur
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from fleet.models import Chauffeur


# --- SECTION 3 : GESTION DES PAIEMENTS ---
def enregistrer_paiement(request, facture_id):
    """Logique pour enregistrer un paiement et mettre à jour le solde client"""
    facture = get_object_or_404(Facture, id=facture_id)
    
    if request.method == "POST":
        montant_paye = float(request.POST.get('montant'))
        
        # Créer l'enregistrement du paiement
        Paiement.objects.create(
            facture=facture, 
            montant=montant_paye,
            mode_paiement=request.POST.get('mode_paiement', 'Espèce')
        )
        
        # Calcul du reste à payer pour mettre à jour le solde
        reste_a_payer = float(facture.montant_TTC) - montant_paye
        
        if reste_a_payer > 0:
            facture.client.solde += reste_a_payer
            facture.client.save()
            facture.statut = 'PARTIEL'
        else:
            facture.statut = 'PAYEE'
        
        facture.save()
        return redirect('liste_factures')

# --- SECTION 6 : ANALYSE ET TABLEAUX DE BORD ---
@login_required
def dashboard_stats(request):
    """Synthèse des données pour les responsables (Graphes et Tableaux)"""
    
    # 1. Analyse Commerciale
    total_ca = Facture.objects.aggregate(Sum('montant_TTC'))['montant_TTC__sum'] or 0
    nb_expeditions = Facture.objects.aggregate(Count('expeditions'))['expeditions__count']
    
    # 2. Top Clients (ceux qui ont le plus de factures)
    top_clients = Client.objects.annotate(
        total_depense=Sum('facture__montant_TTC')
    ).order_by('-total_depense')[:5]

    # 3. Analyse Opérationnelle (Réclamations)
    reclamations_stats = Reclamation.objects.values('statut').annotate(total=Count('id'))

    context = {
        'total_ca': total_ca,
        'nb_expeditions': nb_expeditions,
        'top_clients': top_clients,
        'reclamations_stats': reclamations_stats,
    }
    return render(request, 'Rocket/dashboard.html', context)

# --- LISTE DES FACTURES ---
def liste_factures(request):
    factures = Facture.objects.all().order_by('-date_facture')
    return render(request, 'Rocket/factures_list.html', {'factures': factures})

def signin(request):
    if request.method == "POST":
        # 1. Get Form Data
        role = request.POST.get('role')
        prenom = request.POST.get('first_name')
        nom = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        extra_info = request.POST.get('extra_info')
        # 2. Check if email/username exists
        if Utilisateur.objects.filter(username=email).exists():
            messages.error(request, "⚠️ Cet email est déjà utilisé.")
            return redirect('signin')
        # 3. Create User
        try:
            user = Utilisateur.objects.create_user(
                username=email, # Using email as username
                email=email,
                password=password,
                first_name=prenom,
                last_name=nom,
                role=role.upper() # Ensure matches model choices (ADMIN, AGENT, MANAGER, etc. - verify your model choices)
            )
            # 4. Create Specific Profile
            if role == 'client':
                Client.objects.create(
                    nom=nom,
                    prenom=prenom,
                    email=email,
                    telephone="0000000000", # Placeholder
                    adresse=extra_info if extra_info else "Non renseigné"
                )
            elif role == 'chauffeur':
                Chauffeur.objects.create(
                    nom=nom,
                    prenom=prenom,
                    permis=123456, # Placeholder
                    telephone="0000000000", # Placeholder
                    date_embauche="2024-01-01"
                )

            
            # 5. Log in and Redirect
            login(request, user)
            messages.success(request, "✅ Compte créé avec succès !")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'inscription: {str(e)}")
            
    return render(request, 'Rocket/signin.html')


def login_view(request): # Renamed to login_view to avoid conflict
    if request.method == "POST":
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        
        user = authenticate(request, username=username_input, password=password_input)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "❌ Identifiants invalides.")
            
    return render(request, 'Rocket/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')




