================================================================================
                ROCKET TRANSPORT MANAGEMENT SYSTEM
                      README - Code Source
================================================================================

DESCRIPTION
-----------
Système de gestion de transport et de livraison développé avec Django 5.2.8.
Ce système permet de gérer les expéditions, la facturation, la flotte de 
véhicules, les chauffeurs, et les réclamations clients avec un contrôle 
d'accès basé sur les rôles (RBAC).


PRÉREQUIS
---------
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Environnement virtuel (recommandé)

INSTALLATION
------------

1. Créer un environnement virtuel
   Windows:
     python -m venv venv
     venv\Scripts\activate
   
   macOS/Linux:
     python3 -m venv venv
     source venv/bin/activate

2. Installer Django
   pip install django==5.2.8

3. Appliquer les migrations de base de données
   python manage.py makemigrations
   python manage.py migrate

4. Créer un super-utilisateur (administrateur)
   python manage.py createsuperuser
   
   Suivez les instructions pour définir:
   - Nom d'utilisateur
   - Email
   - Mot de passe

5. (Optionnel) Charger des données initiales
   python manage.py shell
   
   Puis dans le shell Python:
   
   from livraison.models import TypeService, Destination
   
   # Créer les types de service
   TypeService.objects.create(libelle="Standard")
   TypeService.objects.create(libelle="Express")
   TypeService.objects.create(libelle="International")
   
   # Créer des destinations exemple
   Destination.objects.create(
       ville="Alger",
       pays="Algérie",
       zone_geographique="National",
       tarif_base=1000,
       tarif_poids=50,
       tarif_volume=100
   )
   
   Destination.objects.create(
       ville="Oran",
       pays="Algérie",
       zone_geographique="National",
       tarif_base=1200,
       tarif_poids=60,
       tarif_volume=120
   )
   
   exit()

6. Lancer le serveur de développement
   python manage.py runserver

7. Accéder à l'application
   Ouvrez votre navigateur et allez à:
   http://127.0.0.1:8000/

8. Accéder au panneau d'administration Django
   http://127.0.0.1:8000/admin/
   
   Connectez-vous avec les identifiants du super-utilisateur créé à l'étape 4.

STRUCTURE DU PROJET
-------------------

projet_si/
├── Rocket/                 # Application principale
│   ├── views.py           # Logique métier (contrôleurs)
│   ├── urls.py            # Configuration des routes
│   └── ...
├── accounts/              # Gestion des utilisateurs et clients
│   ├── models.py          # Utilisateur, Client, Facture, Paiement, Reclamation
│   └── migrations/
├── livraison/             # Gestion des expéditions
│   ├── models.py          # Expedition, Destination, TypeService, Tarification
│   └── migrations/
├── fleet/                 # Gestion de la flotte
│   ├── models.py          # Chauffeur, Vehicule, Tournee, Incident
│   └── migrations/
├── templates/             # Templates HTML
│   ├── base.html          # Template de base avec navigation
│   └── Rocket/            # Templates spécifiques
│       ├── dashboard.html
│       ├── expedition.html
│       ├── facturation.html
│       ├── database.html
│       ├── incidents.html
│       ├── reclamation.html
│       ├── tournees.html
│       └── tracking.html
├── static/                # Fichiers statiques (CSS, JS, images)
├── projet_si/             # Configuration du projet
│   ├── settings.py        # Paramètres Django
│   ├── urls.py            # Routes principales
│   └── wsgi.py            # Point d'entrée WSGI
├── manage.py              # Script de gestion Django
└── db.sqlite3             # Base de données SQLite (créée après migration)

MODULES PRINCIPAUX
------------------

1. DASHBOARD (/)
   - Tableaux de bord analytiques selon le rôle
   - Métriques commerciales et opérationnelles
   - Graphiques d'évolution mensuelle

2. EXPÉDITIONS (/expedition/)
   - Création d'expéditions avec calcul automatique du coût
   - Liste des expéditions avec filtrage par rôle
   - Suivi en temps réel du statut

3. FACTURATION (/facturation/)
   - Génération de factures groupées
   - Calcul automatique de la TVA (19%)
   - Gestion des paiements partiels/complets
   - Mise à jour automatique du solde client

4. DATABASE (/database/)
   - Gestion des clients, chauffeurs, véhicules, destinations
   - Contrôle d'accès basé sur les rôles
   - Interface CRUD complète

5. TOURNÉES (/tournees/)
   - Planification de tournées multi-expéditions
   - Affectation chauffeur/véhicule
   - Suivi du kilométrage et consommation

6. INCIDENTS (/incidents/)
   - Signalement d'incidents avec preuve
   - Classification par type et gravité
   - Liaison avec expéditions/tournées

7. RÉCLAMATIONS (/reclamation/)
   - Dépôt de réclamations clients
   - Affectation à un agent
   - Suivi de résolution

8. SUIVI (/tracking/<id>/)
   - Historique détaillé d'une expédition
   - Ajout d'étapes de suivi
   - Mise à jour du statut

RÔLES UTILISATEURS
------------------

ADMIN (Administrateur)
- Accès complet à tous les modules
- Droits de création, modification, suppression
- Consultation de tous les tableaux de bord

CLIENT
- Consultation de ses propres expéditions
- Création de nouvelles expéditions
- Dépôt de réclamations
- Gestion limitée de la base de données (clients, destinations)

CHAUFFEUR
- Consultation de ses tournées
- Mise à jour des données de tournée
- Signalement d'incidents
- Gestion limitée de la base de données (chauffeurs, véhicules, destinations)

CRÉATION D'UTILISATEURS
-----------------------

Via le panneau d'administration Django:
1. Accédez à http://127.0.0.1:8000/admin/
2. Connectez-vous avec le compte super-utilisateur
3. Allez dans "Accounts" → "Utilisateurs"
4. Cliquez sur "Ajouter Utilisateur"
5. Remplissez les champs:
   - Username (nom d'utilisateur)
   - Password (mot de passe)
   - Role: ADMIN, CLIENT, ou CHAUFFEUR
   - Email
6. Sauvegardez

Via le shell Django:
python manage.py shell

from accounts.models import Utilisateur

# Créer un admin
admin = Utilisateur.objects.create_user(
    username='admin',
    email='admin@rocket.com',
    password='admin123',
    role='ADMIN',
    is_staff=True
)

# Créer un client
client = Utilisateur.objects.create_user(
    username='client1',
    email='client@example.com',
    password='client123',
    role='CLIENT'
)

# Créer un chauffeur
driver = Utilisateur.objects.create_user(
    username='driver1',
    email='driver@rocket.com',
    password='driver123',
    role='CHAUFFEUR'
)

CONFIGURATION
-------------

Fichier: projet_si/settings.py

Base de données (développement):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

Pour passer en production avec PostgreSQL:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rocket_db',
        'USER': 'votre_utilisateur',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

Modèle utilisateur personnalisé:
AUTH_USER_MODEL = 'accounts.Utilisateur'

Redirection après connexion:
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'index'

COMMANDES UTILES
----------------

# Créer de nouvelles migrations après modification des modèles
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un super-utilisateur
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver

# Lancer le serveur sur un port spécifique
python manage.py runserver 8080

# Ouvrir le shell Django
python manage.py shell

# Collecter les fichiers statiques (production)
python manage.py collectstatic

# Vérifier les problèmes du projet
python manage.py check

TESTS
-----

Pour tester le système:

1. Créez un utilisateur admin, un client, et un chauffeur
2. Testez chaque module avec chaque rôle
3. Vérifiez que les permissions sont correctement appliquées
4. Testez les opérations CRUD sur chaque entité
5. Vérifiez les calculs automatiques (coût, TVA, solde)

DÉPANNAGE
---------

Problème: "No module named 'django'"
Solution: Assurez-vous que Django est installé et que l'environnement virtuel est activé
  pip install django==5.2.8

Problème: "Table doesn't exist"
Solution: Appliquez les migrations
  python manage.py migrate

Problème: "CSRF verification failed"
Solution: Assurez-vous que {% csrf_token %} est présent dans tous les formulaires

Problème: "Permission denied"
Solution: Vérifiez le rôle de l'utilisateur et les permissions dans les vues

SÉCURITÉ
--------

IMPORTANT pour la production:
1. Changez SECRET_KEY dans settings.py
2. Définissez DEBUG = False
3. Configurez ALLOWED_HOSTS avec vos domaines
4. Utilisez HTTPS
5. Configurez une base de données robuste (PostgreSQL)
6. Activez les sauvegardes automatiques
7. Utilisez des mots de passe forts
8. Configurez un pare-feu


LICENCE
-------

Ce projet est développé dans un cadre académique.
Tous droits réservés © 2026

================================================================================
                        Fin du README
================================================================================
