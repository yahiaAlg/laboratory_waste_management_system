# apps/inventory/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Category, Product, StockMovement
from config.resources import CategoryResource, ProductResource, StockMovementResource

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('name', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)

class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    readonly_fields = ('date',)
    fields = ('movement_type', 'quantity', 'reference', 'notes', 'date', 'created_by')
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ('code', 'name', 'category', 'unit_price', 'unit', 'stock_quantity', 'stock_status', 'is_active')
    list_filter = ('category', 'is_service', 'is_active', 'hazard_level')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'stock_status')
    inlines = [StockMovementInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('code', 'name', 'description', 'category', 'is_active')
        }),
        ('Tarification', {
            'fields': ('unit_price', 'unit')
        }),
        ('Gestion de stock', {
            'fields': ('is_service', 'stock_quantity', 'minimum_stock', 'stock_status')
        }),
        ('Spécifications des déchets', {
            'fields': ('hazard_level', 'storage_requirements', 'handling_instructions'),
            'classes': ('collapse',)
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(StockMovement)
class StockMovementAdmin(ImportExportModelAdmin):
    resource_class = StockMovementResource
    list_display = ('product', 'movement_type', 'quantity', 'reference', 'date', 'created_by')
    list_filter = ('movement_type', 'date')
    search_fields = ('product__name', 'product__code', 'reference', 'notes')
    readonly_fields = ('date',)
    
    fieldsets = (
        (None, {
            'fields': ('product', 'movement_type', 'quantity', 'reference', 'notes', 'date', 'created_by')
        }),
    )