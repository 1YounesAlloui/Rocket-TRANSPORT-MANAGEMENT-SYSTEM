from django.db import models
#from livraison.models import Expedition


# Create your models here fleet.

class Chauffeur(models.Model):

    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    permis = models.IntegerField()
    telephone = models.CharField(max_length=50)
    disponibilite = models.BooleanField(default=True)
    date_embauche = models.DateField()

    def __str__(self):
        return f"{self.nom} {self.prenom}"
    

class Vehicule(models.Model):

    immatriculation = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    capacite = models.FloatField()
    etat = models.CharField(max_length=50)

    def __str__(self):
        return self.immatriculation
    
class Tournee(models.Model):
    date_tournee = models.DateField()

    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.PROTECT)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.PROTECT)

    expeditions = models.ManyToManyField('livraison.Expedition', blank=True)


    kilometrage = models.FloatField(null=True, blank=True)
    duree = models.DurationField(null=True, blank=True)
    consommation_carburant = models.FloatField(null=True, blank=True)
    observations = models.TextField(blank=True)

    def __str__(self):
        return f"Tournée {self.id} - {self.date_tournee}"


class Incident(models.Model):
    TYPE_CHOICES = [
        ('Delay', 'Retard'),
        ('Loss', 'Perte'),
        ('Damage', 'Endommagement'),
        ('Technical', 'Problème technique'),
        ('Other', 'Autre'),
    ]
    GRAVITE_CHOICES = [
        ('Basse', 'Basse'),
        ('Moyenne', 'Moyenne'),
        ('Haute', 'Haute'),
    ]

    type_incident = models.CharField(max_length=100, choices=TYPE_CHOICES)
    description = models.TextField()
    date_incident = models.DateField()
    gravite = models.CharField(max_length=50, choices=GRAVITE_CHOICES)

    expedition = models.ForeignKey('livraison.Expedition', on_delete=models.SET_NULL, null=True, blank=True)
    
    tournee = models.ForeignKey(Tournee, on_delete=models.SET_NULL, null=True, blank=True)
    preuve = models.FileField(upload_to='incidents/', null=True, blank=True)
