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
        
        # Only validate if product is set and has required attributes
        if self.product_id and self.product:
            # Check if product has is_service attribute and stock_quantity
            if hasattr(self.product, 'is_service') and hasattr(self.product, 'stock_quantity'):
                # Validate that max_quantity doesn't exceed available stock for physical products
                if not self.product.is_service and self.max_quantity_allowed > self.product.stock_quantity:
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