# apps/customers/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Customer, City, ProductSubscription, SubscriptionUsage
from config.resources import CustomerResource, CityResource, ProductSubscriptionResource, SubscriptionUsageResource

@admin.register(City)
class CityAdmin(ImportExportModelAdmin):
    resource_class = CityResource
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    resource_class = CustomerResource
    list_display = ('name', 'customer_type', 'state', 'phone', 'email', 'is_subscriber', 'is_active')
    list_filter = ('customer_type', 'is_active', 'is_subscriber', 'state')
    search_fields = ('name', 'phone', 'email', 'nif', 'rc')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'customer_type', 'activity', 'is_active')
        }),
        ('Adresse', {
            'fields': ('address_line1', 'address_line2', 'city', 'postal_code', 'state')
        }),
        ('Contact', {
            'fields': ('phone', 'fax', 'email')
        }),
        ('Identifiants légaux', {
            'fields': ('nis', 'rc', 'art', 'nif'),
            'classes': ('collapse',)
        }),
        ('Paramètres commerciaux', {
            'fields': ('credit_limit', 'payment_terms', 'discount_rate')
        }),
        ('Abonnements', {
            'fields': ('is_subscriber',)
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductSubscription)
class ProductSubscriptionAdmin(ImportExportModelAdmin):
    resource_class = ProductSubscriptionResource
    list_display = ('customer', 'product', 'fixed_payment_amount', 'max_quantity_allowed', 'billing_cycle', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'billing_cycle', 'start_date', 'product')
    search_fields = ('customer__name', 'product__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Abonnement', {
            'fields': ('customer', 'product', 'is_active')
        }),
        ('Paramètres financiers', {
            'fields': ('fixed_payment_amount', 'max_quantity_allowed', 'billing_cycle')
        }),
        ('Période', {
            'fields': ('start_date', 'end_date')
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'product')

@admin.register(SubscriptionUsage)
class SubscriptionUsageAdmin(ImportExportModelAdmin):
    resource_class = SubscriptionUsageResource
    list_display = ('subscription', 'quantity_used', 'usage_date', 'reference', 'created_by')
    list_filter = ('usage_date', 'subscription__product', 'subscription__customer')
    search_fields = ('subscription__customer__name', 'subscription__product__name', 'reference')
    readonly_fields = ('created_at',)
    date_hierarchy = 'usage_date'
    
    fieldsets = (
        ('Utilisation', {
            'fields': ('subscription', 'quantity_used', 'usage_date')
        }),
        ('Références', {
            'fields': ('reference', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subscription__customer', 'subscription__product', 'created_by')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)