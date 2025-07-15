from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import calendar

from apps.invoices.models import Invoice, Payment
from apps.customers.models import Customer
from apps.inventory.models import Product
from apps.suppliers.models import Supplier

@login_required
def dashboard_index(request):
    # Date ranges
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Key metrics
    total_customers = Customer.objects.filter(is_active=True).count()
    total_products = Product.objects.filter(is_active=True).count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    
    # Invoice statistics
    total_invoices = Invoice.objects.count()
    pending_invoices = Invoice.objects.filter(status__in=['draft', 'sent']).count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
    
    # Financial metrics
    this_month_revenue = Invoice.objects.filter(
        invoice_date__gte=this_month_start,
        status__in=['sent', 'paid']
    ).aggregate(total=Sum('total_ttc'))['total'] or Decimal('0')
    
    last_month_revenue = Invoice.objects.filter(
        invoice_date__gte=last_month_start,
        invoice_date__lte=last_month_end,
        status__in=['sent', 'paid']
    ).aggregate(total=Sum('total_ttc'))['total'] or Decimal('0')
    
    total_outstanding = Invoice.objects.filter(
        status__in=['sent', 'overdue']
    ).aggregate(total=Sum('total_ttc'))['total'] or Decimal('0')
    
    # Recent invoices
    recent_invoices = Invoice.objects.select_related('customer').order_by('-created_at')[:5]
    
    # Recent payments
    recent_payments = Payment.objects.select_related('invoice', 'invoice__customer').order_by('-created_at')[:5]
    
    # Low stock products
    low_stock_products = Product.objects.filter(
        is_service=False,
        stock_quantity__lte=models.F('minimum_stock'),
        is_active=True
    )[:5]
    
    # Top customers (by revenue)
    top_customers = Customer.objects.annotate(
        total_revenue=Sum('invoice__total_ttc', filter=Q(invoice__status__in=['sent', 'paid']))
    ).filter(total_revenue__isnull=False).order_by('-total_revenue')[:5]
    
    # Monthly revenue chart data (last 12 months) - FIXED using calendar
    monthly_revenue = []
    for i in range(12):
        # Calculate month/year
        if today.month - i <= 0:
            month = 12 + (today.month - i)
            year = today.year - 1
        else:
            month = today.month - i
            year = today.year
        
        # Get month boundaries
        month_start = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        month_end = date(year, month, last_day)
        
        revenue = Invoice.objects.filter(
            invoice_date__gte=month_start,
            invoice_date__lte=month_end,
            status__in=['sent', 'paid']
        ).aggregate(total=Sum('total_ttc'))['total'] or Decimal('0')
        
        monthly_revenue.append({
            'month': month_start.strftime('%B %Y'),
            'revenue': float(revenue)
        })
    
    monthly_revenue.reverse()
    
    # Invoice status distribution
    status_distribution = []
    for status, label in Invoice.STATUS_CHOICES:
        count = Invoice.objects.filter(status=status).count()
        if count > 0:
            status_distribution.append({
                'status': label,
                'count': count
            })
    
    # Debug: Print some values to check
    print(f"This month revenue: {this_month_revenue}")
    print(f"Monthly revenue data: {monthly_revenue}")
    print(f"Total invoices with sent/paid status: {Invoice.objects.filter(status__in=['sent', 'paid']).count()}")
    
    context = {
        'total_customers': total_customers,
        'total_products': total_products,
        'total_suppliers': total_suppliers,
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'overdue_invoices': overdue_invoices,
        'this_month_revenue': this_month_revenue,
        'last_month_revenue': last_month_revenue,
        'total_outstanding': total_outstanding,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments,
        'low_stock_products': low_stock_products,
        'top_customers': top_customers,
        'monthly_revenue': monthly_revenue,
        'status_distribution': status_distribution,
    }
    
    return render(request, 'dashboard/index.html', context)