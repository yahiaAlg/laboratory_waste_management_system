from django.contrib import admin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'city', 'phone', 'email', 'rating', 'is_active')
    list_filter = ('is_active', 'rating', 'city')
    search_fields = ('name', 'contact_person', 'phone', 'email', 'nif', 'rc')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'contact_person', 'services_provided', 'is_active')
        }),
        ('Adresse', {
            'fields': ('address_line1', 'address_line2', 'city', 'postal_code', 'state')
        }),
        ('Contact', {
            'fields': ('phone', 'fax', 'email', 'website')
        }),
        ('Identifiants légaux', {
            'fields': ('rc', 'nis', 'nif'),
            'classes': ('collapse',)
        }),
        ('Paramètres commerciaux', {
            'fields': ('payment_terms', 'rating')
        }),
        ('Contrat', {
            'fields': ('contract_start_date', 'contract_end_date'),
            'classes': ('collapse',)
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )