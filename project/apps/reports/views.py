import json
from pprint import pprint
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv

from apps.invoices.models import Invoice, Payment
from apps.customers.models import Customer
from apps.inventory.models import Product

@login_required
def reports_index(request):
    return render(request, 'reports/index.html')

@login_required
def sales_report(request):
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = timezone.now().replace(day=1).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get sales data
    invoices = Invoice.objects.filter(
        invoice_date__gte=start_date,
        invoice_date__lte=end_date,
        status__in=['sent', 'paid']
    ).select_related('customer')
    
    # Summary statistics
    total_revenue = invoices.aggregate(total=Sum('total_ttc'))['total'] or 0
    total_invoices = invoices.count()
    average_invoice = total_revenue / total_invoices if total_invoices > 0 else 0
    
    # Top customers in period
    top_customers = Customer.objects.annotate(
        period_revenue=Sum('invoice__total_ttc', 
                          filter=Q(invoice__invoice_date__gte=start_date,
                                  invoice__invoice_date__lte=end_date,
                                  invoice__status__in=['sent', 'paid']))
    ).filter(period_revenue__isnull=False).order_by('-period_revenue')[:10]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'invoices': invoices,
        'total_revenue': total_revenue,
        'total_invoices': total_invoices,
        'average_invoice': average_invoice,
        'top_customers': top_customers,
    }
    
    return render(request, 'reports/sales_report.html', context)

@login_required
def customer_report(request):
    customers = Customer.objects.annotate(
        total_revenue=Sum('invoice__total_ttc', filter=Q(invoice__status__in=['sent', 'paid'])),
        invoice_count=Count('invoice', filter=Q(invoice__status__in=['sent', 'paid'])),
        outstanding_balance=Sum('invoice__total_ttc', filter=Q(invoice__status__in=['sent', 'overdue']))
    ).filter(is_active=True)
    
    context = {'customers': customers}
    return render(request, 'reports/customer_report.html', context)

@login_required
def product_report(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    
    products_data = []
    for product in products:
        products_data.append({
            'code': product.code,
            'name': product.name,
            'category': product.category.name,
            'price': float(product.unit_price),
            'stock': float(product.stock_quantity),
            'isService': product.is_service,
            'hazardLevel': product.hazard_level,
            'hazardLevelDisplay': product.get_hazard_level_display(),
            'isActive': product.is_active,
            'isLowStock': product.is_low_stock,
            'unit': product.unit,
        })
    
    context = {'products_data': json.dumps(products_data)}
    return render(request, 'reports/product_report.html', context)

@login_required
def financial_report(request):
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = timezone.now().replace(day=1).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Financial summary
    period_invoices = Invoice.objects.filter(
        invoice_date__gte=start_date,
        invoice_date__lte=end_date
    )
    
    total_invoiced = period_invoices.aggregate(total=Sum('total_ttc'))['total'] or 0
    total_ht = period_invoices.aggregate(total=Sum('subtotal_ht'))['total'] or 0
    total_tva = period_invoices.aggregate(total=Sum('tva_amount'))['total'] or 0
    
    period_payments = Payment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date
    )
    
    total_collected = period_payments.aggregate(total=Sum('amount'))['total'] or 0
    
    outstanding_invoices = Invoice.objects.filter(
        status__in=['sent', 'overdue']
    )
    total_outstanding = outstanding_invoices.aggregate(total=Sum('total_ttc'))['total'] or 0
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_invoiced': total_invoiced,
        'total_ht': total_ht,
        'total_tva': total_tva,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'period_invoices': period_invoices,
        'period_payments': period_payments,
    }
    
    return render(request, 'reports/financial_report.html', context)

@login_required
def export_csv(request, report_type):
    """Export reports to CSV"""
    response = HttpResponse(content_type='text/csv')
    
    if report_type == 'invoices':
        response['Content-Disposition'] = 'attachment; filename="factures.csv"'
        writer = csv.writer(response)
        writer.writerow(['Numéro', 'Date', 'Client', 'Total HT', 'TVA', 'Total TTC', 'Statut'])
        
        invoices = Invoice.objects.select_related('customer').all()
        for invoice in invoices:
            writer.writerow([
                invoice.invoice_number,
                invoice.invoice_date,
                invoice.customer.name,
                invoice.subtotal_ht,
                invoice.tva_amount,
                invoice.total_ttc,
                invoice.get_status_display()
            ])
    
    elif report_type == 'customers':
        response['Content-Disposition'] = 'attachment; filename="clients.csv"'
        writer = csv.writer(response)
        writer.writerow(['Nom', 'Email', 'Téléphone', 'Ville', 'Statut'])
        
        customers = Customer.objects.all()
        for customer in customers:
            writer.writerow([
                customer.name,
                customer.email,
                customer.phone,
                customer.city,
                'Actif' if customer.is_active else 'Inactif'
            ])
    
    elif report_type == 'products':
        response['Content-Disposition'] = 'attachment; filename="produits.csv"'
        writer = csv.writer(response)
        writer.writerow(['Code', 'Nom', 'Catégorie', 'Prix unitaire', 'Stock', 'Statut'])
        
        products = Product.objects.select_related('category').all()
        for product in products:
            writer.writerow([
                product.code,
                product.name,
                product.category.name,
                product.unit_price,
                product.stock_quantity if not product.is_service else 'Service',
                'Actif' if product.is_active else 'Inactif'
            ])
    
    return response