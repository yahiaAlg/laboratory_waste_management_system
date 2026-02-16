# Models Documentation

This document contains all Django models organized by application.

---

## Authentication App

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('manager', 'Gestionnaire'),
        ('operator', 'Opérateur'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='custom_user_set',
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='custom_user_set',
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
```

---

## Company App

```python
from django.db import models

from apps.customers.models import City

class Company(models.Model):
    # Basic information
    name = models.CharField(max_length=200, verbose_name="Raison sociale")
    business_description = models.CharField(max_length=300, blank=True, verbose_name="Description d'activité")

    # Address
    address_line1 = models.CharField(max_length=200, verbose_name="Adresse ligne 1")
    address_line2 = models.CharField(max_length=200, blank=True, verbose_name="Adresse ligne 2")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    state = models.ForeignKey(City, on_delete=models.CASCADE , verbose_name="Wilaya", related_name='companies')

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
```

---

## Customers App

```python
from django.db import models
from django.core.validators import RegexValidator
from apps.inventory.models import Product

class City(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, validators=[RegexValidator(regex='^(\d{3}-\d{4})$')])

    class Meta:
        verbose_name = "cité"
        verbose_name_plural = "cités"

    def __str__(self):
        return self.name


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
    state = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Wilaya", related_name='customers')

    # Contact information - made optional
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    fax = models.CharField(max_length=20, blank=True, verbose_name="Fax")
    email = models.EmailField(blank=True, verbose_name="Email")

    # Business information
    activity = models.CharField(max_length=200, blank=True, verbose_name="Activité")

    # Legal identifiers - made optional
    nis = models.CharField(max_length=20, blank=True, verbose_name="NIS")
    rc = models.CharField(max_length=20, blank=True, verbose_name="RC")
    art = models.CharField(max_length=20, blank=True, verbose_name="ART")
    nif = models.CharField(max_length=20, blank=True, verbose_name="NIF")

    # Commercial settings
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Limite de crédit")
    payment_terms = models.IntegerField(default=30, verbose_name="Délai de paiement (jours)")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taux de remise (%)")

    # Subscription settings
    is_subscriber = models.BooleanField(default=False, verbose_name="Abonné avec offres")

    def has_active_subscriptions(self):
        """Check if customer has any active subscriptions"""
        return self.subscriptions.filter(is_active=True).exists()

    def get_total_subscription_amount(self):
        """Get total monthly subscription amount for all active subscriptions"""
        from django.db.models import Sum
        return self.subscriptions.filter(is_active=True).aggregate(
            total=Sum('fixed_payment_amount')
        )['total'] or 0

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


class ProductSubscription(models.Model):
    """Represents a customer's subscription to a specific product with fixed payment"""

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Client", related_name='subscriptions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    fixed_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant forfaitaire")
    max_quantity_allowed = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité maximale autorisée")

    # Status and dates
    is_active = models.BooleanField(default=True, verbose_name="Abonnement actif")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")

    # Billing cycle
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ]
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly', verbose_name="Cycle de facturation")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Abonnement produit"
        verbose_name_plural = "Abonnements produits"
        unique_together = ['customer', 'product']  # One subscription per product per customer
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} ({self.fixed_payment_amount})"

    def clean(self):
        from django.core.exceptions import ValidationError

        # Only validate if product is set and has required attributes AND max_quantity_allowed is not None
        if self.product_id and self.product and self.max_quantity_allowed is not None:
            # Check if product has is_service attribute and stock_quantity
            if hasattr(self.product, 'is_service') and hasattr(self.product, 'stock_quantity'):
                # Validate that max_quantity doesn't exceed available stock for physical products
                if (not self.product.is_service and
                    self.product.stock_quantity is not None and
                    self.max_quantity_allowed > self.product.stock_quantity):
                    raise ValidationError(
                        f"La quantité maximale ({self.max_quantity_allowed}) ne peut pas dépasser le stock disponible ({self.product.stock_quantity})"
                    )

    @property
    def remaining_quantity(self):
        """Calculate remaining quantity for current billing period"""
        from django.utils import timezone

        # Get current period start date
        today = timezone.now().date()
        if self.billing_cycle == 'monthly':
            period_start = today.replace(day=1)
        elif self.billing_cycle == 'quarterly':
            quarter = (today.month - 1) // 3
            period_start = today.replace(month=quarter * 3 + 1, day=1)
        else:  # yearly
            period_start = today.replace(month=1, day=1)

        # Calculate used quantity in current period
        used_quantity = SubscriptionUsage.objects.filter(
            subscription=self,
            usage_date__gte=period_start,
            usage_date__lte=today
        ).aggregate(total=models.Sum('quantity_used'))['total'] or 0

        return max(0, self.max_quantity_allowed - used_quantity)


class SubscriptionUsage(models.Model):
    """Track usage of subscribed products"""

    subscription = models.ForeignKey(ProductSubscription, on_delete=models.CASCADE, verbose_name="Abonnement", related_name='usages')
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité utilisée")
    usage_date = models.DateField(verbose_name="Date d'utilisation")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence (commande, facture)")
    notes = models.TextField(blank=True, verbose_name="Notes")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE, verbose_name="Créé par")

    class Meta:
        verbose_name = "Utilisation d'abonnement"
        verbose_name_plural = "Utilisations d'abonnements"
        ordering = ['-usage_date']

    def __str__(self):
        return f"{self.subscription} - {self.quantity_used} le {self.usage_date}"

    def clean(self):
        from django.core.exceptions import ValidationError

        # Check if usage exceeds remaining quantity
        remaining = self.subscription.remaining_quantity
        if self.quantity_used > remaining:
            raise ValidationError(
                f"La quantité utilisée ({self.quantity_used}) dépasse la quantité restante ({remaining})"
            )
```

---

## Inventory App

```python
from django.db import models
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    UNIT_CHOICES = [
        ('KG', 'Kilogramme'),
        ('TONNE', 'Tonne'),
        ('LITRE', 'Litre'),
        ('PIECE', 'Pièce'),
        ('SERVICE', 'Service'),
        ('HEURE', 'Heure'),
        ('JOUR', 'Jour'),
    ]

    HAZARD_LEVELS = [
        ('none', 'Aucun'),
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ]

    # Basic information
    code = models.CharField(max_length=50, unique=True, verbose_name="Code produit/service")
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Catégorie")

    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Prix unitaire HT")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='KG', verbose_name="Unité")

    # Stock management (for physical products)
    is_service = models.BooleanField(default=False, verbose_name="Est un service")
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Quantité en stock")
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Stock minimum")

    # Waste-specific fields
    hazard_level = models.CharField(max_length=20, choices=HAZARD_LEVELS, default='none', verbose_name="Niveau de danger")
    storage_requirements = models.TextField(blank=True, verbose_name="Exigences de stockage")
    handling_instructions = models.TextField(blank=True, verbose_name="Instructions de manipulation")

    # Status
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit/Service"
        verbose_name_plural = "Produits/Services"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_low_stock(self):
        return not self.is_service and self.stock_quantity <= self.minimum_stock

    @property
    def stock_status(self):
        if self.is_service:
            return "Service"
        elif self.is_low_stock:
            return "Stock faible"
        elif self.stock_quantity == 0:
            return "Rupture"
        else:
            return "En stock"

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Entrée'),
        ('out', 'Sortie'),
        ('adjustment', 'Ajustement'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, verbose_name="Type de mouvement")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    notes = models.TextField(blank=True, verbose_name="Notes")

    # Timestamps
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE, verbose_name="Créé par")

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-date']

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity}"
```

---

## Invoices App

```python
from datetime import timezone
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

    class PaymentMethods(models.TextChoices):
        CASH = 'cash', 'ESPÈCE'
        CHECK = 'check', 'CHÈQUE'
        TRANSFER = 'transfer', 'VIREMENT'
        CARD = 'card', 'CARTE'

    # Invoice identification
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")

    # Dates
    invoice_date = models.DateField(verbose_name="Date de facture")
    due_date = models.DateField(verbose_name="Date d'échéance")

    # Customer information
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Client")

    # Payment information
    payment_method = models.CharField(max_length=20, choices=PaymentMethods.choices, default='check', verbose_name="Mode de règlement")

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

    def calculate_timbre_fiscal(self, amount_ht_plus_tva):
        """
        Calculate timbre fiscal based on the amount (HT + TVA)

        Rules:
        - If amount < 300: timbre = 5 (constant)
        - If 300 <= amount < 30000: rate = 1%
        - If 30000 <= amount < 100000: rate = 1.5%
        - If amount >= 100000: rate = 2%
        """
        if amount_ht_plus_tva < 300:
            return Decimal('5.00')
        elif amount_ht_plus_tva < 30000:
            return amount_ht_plus_tva * Decimal('0.01')  # 1%
        elif amount_ht_plus_tva < 100000:  # Assuming 10000 was a typo and should be 100000
            return amount_ht_plus_tva * Decimal('0.015')  # 1.5%
        else:
            return amount_ht_plus_tva * Decimal('0.02')  # 2%

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

        if self.payment_method == self.PaymentMethods.CASH:
            # Calculate timbre fiscal based on (HT + TVA)
            amount_ht_plus_tva = discounted_subtotal + self.tva_amount
            self.timbre_fiscal = self.calculate_timbre_fiscal(amount_ht_plus_tva)
        else:
            self.timbre_fiscal = Decimal('0.00')

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
    line_date = models.DateTimeField(verbose_name="Date d'ajout", null=True, blank=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le", null=True, blank=True)
    updated_at = models.DateTimeField(verbose_name="Modifié le", auto_now=True, null=True, blank=True)
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
```

---

## Suppliers App

```python
from django.db import models

from apps.customers.models import City

class Supplier(models.Model):
    # Basic information
    name = models.CharField(max_length=200, verbose_name="Nom/Raison sociale")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Personne de contact")

    # Address
    address_line1 = models.CharField(max_length=200, verbose_name="Adresse ligne 1")
    address_line2 = models.CharField(max_length=200, blank=True, verbose_name="Adresse ligne 2")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    state = models.ForeignKey(City, on_delete=models.CASCADE , verbose_name="Wilaya", related_name='suppliers')

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
```

---

_Note: Dashboard and Reports apps do not have models.py files._
