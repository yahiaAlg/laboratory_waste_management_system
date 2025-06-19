from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from decimal import Decimal
import json

from .models import Invoice, InvoiceLine, Payment
from .forms import InvoiceForm, InvoiceLineFormSet, PaymentForm
from apps.customers.models import Customer
from apps.inventory.models import Product
from apps.company.models import Company

@login_required
def invoice_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    invoices = Invoice.objects.select_related('customer').all()
    
    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    paginator = Paginator(invoices, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Invoice.STATUS_CHOICES,
    }
    return render(request, 'invoices/invoice_list.html', context)

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    payments = Payment.objects.filter(invoice=invoice)
    total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    balance_due = invoice.total_ttc - total_paid
    
    context = {
        'invoice': invoice,
        'payments': payments,
        'total_paid': total_paid,
        'balance_due': balance_due,
    }
    return render(request, 'invoices/invoice_detail.html', context)

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceLineFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            
            formset.instance = invoice
            formset.save()
            
            messages.success(request, f'Facture {invoice.invoice_number} créée avec succès.')
            return redirect('invoices:detail', pk=invoice.pk)
    else:
        form = InvoiceForm(initial={
            'invoice_date': timezone.now().date(),
            'due_date': timezone.now().date() + timezone.timedelta(days=30)
        })
        formset = InvoiceLineFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Créer une facture'
    }
    return render(request, 'invoices/invoice_form.html', context)

@login_required
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if invoice.status == 'paid':
        messages.error(request, 'Impossible de modifier une facture payée.')
        return redirect('invoices:detail', pk=invoice.pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceLineFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.save()
            
            messages.success(request, f'Facture {invoice.invoice_number} modifiée avec succès.')
            return redirect('invoices:detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceLineFormSet(instance=invoice)
    
    context = {
        'form': form,
        'formset': formset,
        'invoice': invoice,
        'title': 'Modifier la facture'
    }
    return render(request, 'invoices/invoice_form.html', context)

@login_required
def invoice_print(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    company = Company.objects.first()
    
    context = {
        'invoice': invoice,
        'company': company,
    }
    return render(request, 'invoices/invoice_print.html', context)

@login_required
def add_payment(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.created_by = request.user
            payment.save()
            
            # Update invoice status if fully paid
            payments_total = Payment.objects.filter(invoice=invoice).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            if payments_total >= invoice.total_ttc:
                invoice.status = 'paid'
                invoice.save()
            
            messages.success(request, 'Paiement enregistré avec succès.')
            return redirect('invoices:detail', pk=invoice.pk)
    else:
        # Calculate remaining balance
        payments_total = Payment.objects.filter(invoice=invoice).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        remaining_balance = invoice.total_ttc - payments_total
        
        form = PaymentForm(initial={
            'amount': remaining_balance,
            'payment_date': timezone.now().date(),
            'payment_method': invoice.payment_method
        })
    
    context = {
        'form': form,
        'invoice': invoice,
        'title': 'Ajouter un paiement'
    }
    return render(request, 'invoices/payment_form.html', context)

@login_required
def get_product_data(request):
    """AJAX view to get product data for invoice lines"""
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            product = Product.objects.get(pk=product_id)
            data = {
                'description': product.name,
                'unit': product.unit,
                'unit_price': str(product.unit_price),
                'code': product.code,
            }
            return JsonResponse(data)
        except Product.DoesNotExist:
            pass
    
    return JsonResponse({'error': 'Product not found'}, status=404)

@login_required
def invoice_status_update(request, pk):
    """Update invoice status"""
    if request.method == 'POST':
        invoice = get_object_or_404(Invoice, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Invoice.STATUS_CHOICES):
            invoice.status = new_status
            invoice.save()
            messages.success(request, f'Statut de la facture mis à jour: {invoice.get_status_display()}')
        
        return redirect('invoices:detail', pk=invoice.pk)