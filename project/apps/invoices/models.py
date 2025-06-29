from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.customers.models import Customer
from apps.inventory.models import Product
from apps.company.models import Company

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
        ('cancelled', 'Annulée'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'ESPÈCE'),
        ('check', 'CHÈQUE'),
        ('transfer', 'VIREMENT'),
        ('card', 'CARTE'),
    ]
    
    # Invoice identification
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    
    # Dates
    invoice_date = models.DateField(verbose_name="Date de facture")
    due_date = models.DateField(verbose_name="Date d'échéance")
    
    # Customer information
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Client")
    
    # Payment information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='check', verbose_name="Mode de règlement")
    
    # Logistics information
    driver_name = models.CharField(max_length=100, blank=True, verbose_name="Chauffeur")
    vehicle_registration = models.CharField(max_length=20, blank=True, verbose_name="Matricule véhicule")
    destination = models.CharField(max_length=200, blank=True, verbose_name="Destination")
    
    # Financial fields
    subtotal_ht = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total HT")
    tva_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant TVA")
    timbre_fiscal = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Timbre")
    other_taxes = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Autres taxes")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Remise")
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total TTC")
    
    # Status and notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE, verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-invoice_date', '-created_at']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            company = Company.objects.first()
            if company:
                self.invoice_number = company.get_next_invoice_number()
        
        # Only calculate totals if the invoice already exists (has a primary key)
        if self.pk:
            self.calculate_totals()
        
        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculate invoice totals based on line items"""
        if not self.pk:
            # Can't calculate totals for unsaved invoice
            return
            
        line_items = self.invoiceline_set.all()
        
        # Calculate subtotal
        self.subtotal_ht = sum(line.line_total for line in line_items)
        
        # Apply discount
        if self.discount_amount > 0:
            discounted_subtotal = self.subtotal_ht - self.discount_amount
        else:
            discounted_subtotal = self.subtotal_ht
        
        # Check if customer has legal information for TVA calculation
        customer_has_legal_info = bool(
            self.customer.nis or 
            self.customer.rc or 
            self.customer.art or
            self.customer.nif
        )
        
        # Calculate TVA only if customer has legal information
        if customer_has_legal_info:
            company = Company.objects.first()
            tva_rate = company.tva_rate if company else Decimal('19.00')
            self.tva_amount = discounted_subtotal * (tva_rate / 100)
        else:
            self.tva_amount = Decimal('0.00')
        
        # Calculate total
        self.total_ttc = discounted_subtotal + self.tva_amount + self.timbre_fiscal + self.other_taxes

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.status != 'paid' and self.due_date < timezone.now().date()

class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Facture")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit/Service")
    
    # Line details
    reference = models.CharField(max_length=50, blank=True, verbose_name="Référence")
    description = models.CharField(max_length=500, verbose_name="Désignation")
    unit = models.CharField(max_length=20, verbose_name="Unité")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Prix unitaire HT")
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant HT")
    
    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Trigger invoice total recalculation
        self.invoice.calculate_totals()
        self.invoice.save()
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Espèces'),
        ('check', 'Chèque'),
        ('transfer', 'Virement'),
        ('card', 'Carte bancaire'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Facture")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Montant")
    payment_date = models.DateField(verbose_name="Date de paiement")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="Mode de paiement")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE, verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.amount} DA"