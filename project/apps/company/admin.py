from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone', 'email')
    search_fields = ('name', 'city', 'phone', 'email', 'nif', 'rc')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'business_description', 'logo')
        }),
        ('Adresse', {
            'fields': ('address_line1', 'address_line2', 'city', 'postal_code', 'state')
        }),
        ('Contact', {
            'fields': ('phone', 'fax', 'email', 'website')
        }),
        ('Informations légales', {
            'fields': ('capital_social', 'rc', 'art', 'nis', 'nif', 'rib')
        }),
        ('Paramètres de facturation', {
            'fields': ('tva_rate', 'timbre_fiscal', 'invoice_prefix', 'next_invoice_number')
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )