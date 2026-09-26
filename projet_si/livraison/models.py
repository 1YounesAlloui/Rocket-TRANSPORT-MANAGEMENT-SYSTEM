from django.db import models
from django.utils import timezone

# Create your models here livraison.

class Destination(models.Model):
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    zone_geographique = models.CharField(max_length=100)
    tarif_base = models.FloatField(default=0.0)
    tarif_poids = models.FloatField(default=0.0)
    tarif_volume = models.FloatField(default=0.0)
    tarif_forfaitaire = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.ville} - {self.pays}"
    


class TypeService(models.Model):
    libelle = models.CharField(max_length=50)
    tarif_poids = models.FloatField(default=0.0)
    tarif_volume = models.FloatField(default=0.0)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.libelle
    

class Tarification(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    type_service = models.ForeignKey(TypeService, on_delete=models.CASCADE)
    tarif_base = models.FloatField(default=0.0)
    tarif_poids = models.FloatField(default=0.0)
    tarif_volume = models.FloatField(default=0.0)
    tarif_forfaitaire = models.FloatField(default=0.0)

    def __str__(self):
      return f"{self.destination} - {self.type_service}"
    


class Expedition(models.Model):
    
    STATUT_CHOICES = [
        ('Enregistré', 'Enregistré'),
        ('En transit', 'En transit'),
        ('Tri en cours', 'Centre de tri'),
        ('En livraison', 'En cours de livraison'),
        ('Livré', 'Livré'),
        ('Échec', 'Échec'),
    ]

    numero_expedition = models.CharField(max_length=20, unique=True)
    poids = models.FloatField()
    volume = models.FloatField()
    description = models.TextField(blank=True)
    montant_total = models.FloatField(editable=False)
    date_creation = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES)

    client = models.ForeignKey('accounts.Client', on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT)
    type_service = models.ForeignKey(TypeService, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        # Auto-generate unique number if not set
        if not self.numero_expedition:
            last = Expedition.objects.order_by('id').last()
            new_id = (last.id + 1) if last else 1
            self.numero_expedition = f"EXP-{timezone.now().year}-{new_id:04d}"

        # Only calculate if not explicitly set (to allow view-based overrides if needed)
        if self.montant_total is None or self.montant_total == 0:
            try:
                tarification = Tarification.objects.get(
                    destination=self.destination,
                    type_service=self.type_service
                )
                self.montant_total = (
                    tarification.tarif_base +
                    (self.poids * tarification.tarif_poids) +
                    (self.volume * tarification.tarif_volume)
                )
            except Tarification.DoesNotExist:
                # Fallback to a basic rate or keep it at 0
                self.montant_total = 1000 + (self.poids * 100) + (self.volume * 200)

        super().save(*args, **kwargs)

    @property
    def in_tour(self):
        return self.tournee_set.exists()

    def __str__(self):
        return self.numero_expedition
    

class SuiviExpedition(models.Model):
    expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE, related_name='tracking_history')
    date_etape = models.DateTimeField(default=timezone.now)
    lieu = models.CharField(max_length=100)
    statut_etape = models.CharField(max_length=50)
    commentaire = models.TextField(blank=True)

    def __str__(self):
        return f"{self.expedition.numero_expedition} - {self.statut_etape}"

