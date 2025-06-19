from django.db import models
from django.core.validators import RegexValidator

class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Particulier'),
        ('company', 'Entreprise'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom/Raison sociale")
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='company', verbose_name="Type de client")
    
    # Address information
    address_line1 = models.CharField(max_length=200, verbose_name="Adresse ligne 1")
    address_line2 = models.CharField(max_length=200, blank=True, verbose_name="Adresse ligne 2")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    state = models.CharField(max_length=100, default="Algérie", verbose_name="Wilaya/État")
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    fax = models.CharField(max_length=20, blank=True, verbose_name="Fax")
    email = models.EmailField(blank=True, verbose_name="Email")
    
    # Business information
    activity = models.CharField(max_length=200, blank=True, verbose_name="Activité")
    
    # Legal identifiers
    nis = models.CharField(max_length=20, blank=True, verbose_name="NIS")
    rc = models.CharField(max_length=20, blank=True, verbose_name="RC")
    art = models.CharField(max_length=20, blank=True, verbose_name="ART")
    nif = models.CharField(max_length=20, blank=True, verbose_name="NIF")
    
    # Commercial settings
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Limite de crédit")
    payment_terms = models.IntegerField(default=30, verbose_name="Délai de paiement (jours)")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taux de remise (%)")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_address(self):
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        address_parts.append(f"{self.postal_code} {self.city}")
        return ", ".join(address_parts)