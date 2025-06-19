from django.db import models

class Supplier(models.Model):
    # Basic information
    name = models.CharField(max_length=200, verbose_name="Nom/Raison sociale")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Personne de contact")
    
    # Address
    address_line1 = models.CharField(max_length=200, verbose_name="Adresse ligne 1")
    address_line2 = models.CharField(max_length=200, blank=True, verbose_name="Adresse ligne 2")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    state = models.CharField(max_length=100, default="Algérie", verbose_name="Wilaya/État")
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    fax = models.CharField(max_length=20, blank=True, verbose_name="Fax")
    email = models.EmailField(blank=True, verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Site web")
    
    # Business information
    services_provided = models.TextField(blank=True, verbose_name="Services fournis")
    
    # Legal identifiers
    rc = models.CharField(max_length=20, blank=True, verbose_name="RC")
    nis = models.CharField(max_length=20, blank=True, verbose_name="NIS")
    nif = models.CharField(max_length=20, blank=True, verbose_name="NIF")
    
    # Commercial settings
    payment_terms = models.IntegerField(default=30, verbose_name="Délai de paiement (jours)")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=3, verbose_name="Évaluation")
    
    # Contract information
    contract_start_date = models.DateField(blank=True, null=True, verbose_name="Date début contrat")
    contract_end_date = models.DateField(blank=True, null=True, verbose_name="Date fin contrat")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
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