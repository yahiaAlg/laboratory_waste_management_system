# templatetags/custom_filters.py
import decimal
from django import template
from django.db.models import Sum
from decimal import Decimal

register = template.Library()

@register.simple_tag
def get_remaining_balance(invoice):
    """
    Calculate the remaining balance for an invoice
    Usage: {% get_remaining_balance invoice as remaining_balance %}
    """
    from apps.invoices.models import Payment
    
    # Get total paid amount for this invoice
    paid_amount = Payment.objects.filter(invoice=invoice).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0')
    
    # Calculate remaining balance
    remaining_balance = invoice.total_ttc - paid_amount
    
    return remaining_balance

@register.filter
def remaining_balance(invoice):
    """
    Filter version to get remaining balance
    Usage: {{ invoice|remaining_balance }}
    """
    from apps.invoices.models import Payment
    
    paid_amount = Payment.objects.filter(invoice=invoice).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0')
    
    return invoice.total_ttc - paid_amount

@register.filter
def total_paid(invoice):
    """
    Get total paid amount for an invoice
    Usage: {{ invoice|total_paid }}
    """
    from apps.invoices.models import Payment
    
    return Payment.objects.filter(invoice=invoice).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0')

@register.filter
def payment_percentage(invoice):
    """
    Get payment completion percentage
    Usage: {{ invoice|payment_percentage }}
    """
    from apps.invoices.models import Payment
    
    if invoice.total_ttc == 0:
        return 0
    
    paid_amount = Payment.objects.filter(invoice=invoice).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0')
    
    percentage = (paid_amount / invoice.total_ttc) * 100
    return round(percentage, 1)

@register.filter
def is_fully_paid(invoice):
    """
    Check if invoice is fully paid
    Usage: {% if invoice|is_fully_paid %}
    """
    from apps.invoices.models import Payment
    
    paid_amount = Payment.objects.filter(invoice=invoice).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0')
    
    return paid_amount >= invoice.total_ttc

@register.filter
def has_payments(invoice):
    """
    Check if invoice has any payments
    Usage: {% if invoice|has_payments %}
    """
    from apps.invoices.models import Payment
    
    return Payment.objects.filter(invoice=invoice).exists()

@register.filter
def payment_count(invoice):
    """
    Get number of payments for an invoice
    Usage: {{ invoice|payment_count }}
    """
    from apps.invoices.models import Payment
    
    return Payment.objects.filter(invoice=invoice).count()

@register.filter
def format_currency(amount):
    """
    Format amount as currency
    Usage: {{ amount|format_currency }}
    """
    if amount is None:
        return "0.00 DA"
    
    return f"{amount:,.2f} DA"

@register.filter
def payment_method_icon(method):
    """
    Get icon for payment method
    Usage: {{ payment.payment_method|payment_method_icon }}
    """
    icons = {
        'cash': '💵',
        'check': '📄',
        'transfer': '🏦',
        'card': '💳',
    }
    return icons.get(method, '💰')

@register.filter
def payment_method_class(method):
    """
    Get CSS class for payment method badge
    Usage: class="method-{{ payment.payment_method|payment_method_class }}"
    """
    return method  # Returns 'cash', 'check', 'transfer', 'card'

@register.filter
def status_badge_class(status):
    """
    Get Bootstrap badge class for invoice status
    Usage: class="badge bg-{{ invoice.status|status_badge_class }}"
    """
    classes = {
        'draft': 'secondary',
        'sent': 'primary',
        'paid': 'success',
        'overdue': 'danger',
        'cancelled': 'dark',
    }
    return classes.get(status, 'secondary')

@register.filter
def subtract(value, arg):
    """
    Subtract arg from value
    Usage: {{ total|subtract:discount }}
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """
    Multiply value by arg
    Usage: {{ price|multiply:quantity }}
    """
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, decimal.InvalidOperation):
        return Decimal('0')

@register.filter
def percentage_of(value, total):
    """
    Calculate percentage of value from total
    Usage: {{ paid|percentage_of:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.simple_tag
def get_invoice_summary(invoice):
    """
    Get comprehensive invoice summary
    Usage: {% get_invoice_summary invoice as summary %}
    """
    from apps.invoices.models import Payment
    
    payments = Payment.objects.filter(invoice=invoice)
    total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    remaining = invoice.total_ttc - total_paid
    
    return {
        'total_amount': invoice.total_ttc,
        'total_paid': total_paid,
        'remaining_balance': remaining,
        'payment_count': payments.count(),
        'payment_percentage': round((total_paid / invoice.total_ttc) * 100, 1) if invoice.total_ttc > 0 else 0,
        'is_fully_paid': total_paid >= invoice.total_ttc,
        'is_partially_paid': 0 < total_paid < invoice.total_ttc,
        'has_payments': payments.exists(),
    }

@register.inclusion_tag('invoices/tags/payment_status_badge.html')
def payment_status_badge(invoice):
    """
    Render payment status badge
    Usage: {% payment_status_badge invoice %}
    """
    from apps.invoices.models import Payment
    
    paid_amount = Payment.objects.filter(invoice=invoice).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0')
    
    percentage = (paid_amount / invoice.total_ttc) * 100 if invoice.total_ttc > 0 else 0
    
    if percentage >= 100:
        status = 'paid'
        class_name = 'success'
        text = 'Payé'
    elif percentage > 0:
        status = 'partial'
        class_name = 'warning'
        text = f'Partiel ({percentage:.0f}%)'
    else:
        status = 'unpaid'
        class_name = 'danger'
        text = 'Non payé'
    
    return {
        'status': status,
        'class_name': class_name,
        'text': text,
        'percentage': percentage,
    }