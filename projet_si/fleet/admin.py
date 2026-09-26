from django.contrib import admin
from .models import Chauffeur, Vehicule, Tournee, Incident

# Register your models here.

admin.site.register(Chauffeur)
admin.site.register(Vehicule)
admin.site.register(Tournee)
admin.site.register(Incident)

