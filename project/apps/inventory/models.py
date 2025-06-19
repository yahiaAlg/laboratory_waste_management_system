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