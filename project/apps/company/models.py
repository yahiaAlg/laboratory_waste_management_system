from django.db import models

class Company(models.Model):
    # Basic information
    name = models.CharField(max_length=200, verbose_name="Raison sociale")
    business_description = models.CharField(max_length=300, blank=True, verbose_name="Description d'activité")
    
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
    
    # Legal information
    capital_social = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Capital social")
    rc = models.CharField(max_length=50, blank=True, verbose_name="RC (Registre de Commerce)")
    art = models.CharField(max_length=50, blank=True, verbose_name="ART")
    nis = models.CharField(max_length=50, blank=True, verbose_name="NIS")
    nif = models.CharField(max_length=50, blank=True, verbose_name="NIF")
    rib = models.CharField(max_length=50, blank=True, verbose_name="RIB")
    
    # Logo and branding
    logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name="Logo")
    
    # Tax settings
    tva_rate = models.DecimalField(max_digits=5, decimal_places=2, default=19.00, verbose_name="Taux TVA (%)")
    timbre_fiscal = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Timbre fiscal")
    
    # Invoice settings
    invoice_prefix = models.CharField(max_length=10, default="FACT", verbose_name="Préfixe facture")
    next_invoice_number = models.PositiveIntegerField(default=1, verbose_name="Prochain numéro de facture")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
    
    def __str__(self):
        return self.name
    
    @property
    def full_address(self):
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        address_parts.append(f"{self.postal_code} {self.city}")
        return "\n".join(address_parts)
    
    def get_next_invoice_number(self):
        """Get and increment the next invoice number"""
        current_number = self.next_invoice_number
        self.next_invoice_number += 1
        self.save(update_fields=['next_invoice_number'])
        return f"{self.invoice_prefix}{current_number:05d}"