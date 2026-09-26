from django.db import models
from django.contrib.auth.models import AbstractUser

#models.py accounts.
class Utilisateur(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrateur'), 
        ('CLIENT', 'Client'),        
        ('CHAUFFEUR', 'Chauffeur'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='')

class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    solde = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Facture(models.Model):
    STATUTS = (('PAYEE', 'Payée'), ('PARTIEL', 'Partiel'), ('IMPAYEE', 'Impayée'))
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    expeditions = models.ManyToManyField('livraison.Expedition') 
    date_facture = models.DateTimeField(auto_now_add=True)
    montant_HT = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_TVA = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_TTC = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=10, choices=STATUTS, default='IMPAYEE')

class Paiement(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    date_paiement = models.DateTimeField(auto_now_add=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=50)

class Reclamation(models.Model):
    STATUTS = (('EN_COURS', 'En cours'), ('RESOLUE', 'Résolue'), ('ANNULEE', 'Annulée'))
    date = models.DateTimeField(auto_now_add=True)
    objet = models.CharField(max_length=200)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    
    # Section 5 Requirements
    expeditions = models.ManyToManyField('livraison.Expedition', blank=True)
    facture = models.ForeignKey(Facture, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_reclamations')
    
    statut = models.CharField(max_length=20, choices=STATUTS, default='EN_COURS')
    commentaire = models.TextField()

    def __str__(self):
        return f"RECL-{self.id} : {self.objet}"