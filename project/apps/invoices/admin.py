from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, InvoiceLine, Payment

class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1
    fields = ('product', 'description', 'quantity', 'unit', 'unit_price', 'line_total')
    readonly_fields = ('line_total',)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('payment_date', 'amount', 'payment_method', 'reference', 'notes', 'created_by', 'created_at')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'invoice_date', 'due_date', 'total_ttc', 'status_colored', 'created_by')
    list_filter = ('status', 'invoice_date', 'due_date', 'payment_method')
    search_fields = ('invoice_number', 'customer__name', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'subtotal_ht', 'total_ttc')
    inlines = [InvoiceLineInline, PaymentInline]
    
    fieldsets = (
        ('Identification', {
            'fields': ('invoice_number', 'status')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date')
        }),
        ('Client', {
            'fields': ('customer',)
        }),
        ('Paiement', {
            'fields': ('payment_method',)
        }),
        ('Logistique', {
            'fields': ('driver_name', 'vehicle_registration', 'destination'),
            'classes': ('collapse',)
        }),
        ('Totaux', {
            'fields': ('subtotal_ht', 'tva_amount', 'timbre_fiscal', 'other_taxes', 'discount_amount', 'total_ttc')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'draft': 'blue',
            'sent': 'orange',
            'paid': 'green',
            'overdue': 'red',
            'cancelled': 'gray',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Statut'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_date', 'payment_method', 'reference', 'created_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('invoice__invoice_number', 'reference', 'notes')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('invoice', 'amount', 'payment_date', 'payment_method', 'reference', 'notes')
        }),
        ('Horodatage', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )