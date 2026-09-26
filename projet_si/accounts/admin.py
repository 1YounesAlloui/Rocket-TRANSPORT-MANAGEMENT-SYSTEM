from django.contrib import admin
from .models import Utilisateur, Client, Facture, Paiement, Reclamation

admin.site.register(Utilisateur)
admin.site.register(Client)
admin.site.register(Facture)
admin.site.register(Paiement)
admin.site.register(Reclamation)