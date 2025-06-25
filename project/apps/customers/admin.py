# apps/customers/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Customer, City
from config.resources import CustomerResource, CityResource

@admin.register(City)
class CityAdmin(ImportExportModelAdmin):
    resource_class = CityResource
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    resource_class = CustomerResource
    list_display = ('name', 'customer_type', 'city', 'phone', 'email', 'is_active')
    list_filter = ('customer_type', 'is_active', 'city')
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
        ('Horodatage', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )