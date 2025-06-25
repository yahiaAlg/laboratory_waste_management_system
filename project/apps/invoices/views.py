from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal

from .models import Invoice, Payment
from .forms import InvoiceForm, InvoiceLineFormSet, PaymentForm
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
def invoice_create(request):
    company = Company.objects.first()
    products = Product.objects.filter(is_active=True).order_by('code', 'name')  # Add this line
    
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
        'company': company,
        'products': products,  # Add this line
        'title': 'Créer une facture'
    }
    return render(request, 'invoices/invoice_form.html', context)

@login_required
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    company = Company.objects.first()
    products = Product.objects.filter(is_active=True).order_by('code', 'name')  # Add this line
    
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
        'company': company,
        'products': products,  # Add this line
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
def get_product_data(request):
    """AJAX view to get product data for invoice lines"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    product_id = request.GET.get('product_id')
    
    if not product_id:
        return JsonResponse({'error': 'Product ID is required'}, status=400)
    
    try:
        product_id = int(product_id)
        product = Product.objects.get(pk=product_id)
        
        data = {
            'success': True,
            'description': product.name,
            'unit': product.unit,
            'unit_price': str(product.unit_price),
            'code': product.code,
        }
        return JsonResponse(data)
        
    except ValueError:
        return JsonResponse({'error': 'Invalid product ID format'}, status=400)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Server error occurred'}, status=500)

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


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    payments = Payment.objects.filter(invoice=invoice).order_by('-payment_date', '-created_at')
    total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    balance_due = invoice.total_ttc - total_paid
    
    # Update invoice status based on payments
    if total_paid >= invoice.total_ttc and invoice.status != 'paid':
        invoice.status = 'paid'
        invoice.save()
    elif total_paid > 0 and total_paid < invoice.total_ttc and invoice.status == 'draft':
        invoice.status = 'sent'
        invoice.save()
    
    context = {
        'invoice': invoice,
        'payments': payments,
        'total_paid': total_paid,
        'balance_due': balance_due,
        'payments_count': payments.count(),
    }
    return render(request, 'invoices/invoice_detail.html', context)

@login_required
def add_payment(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    # Calculate remaining balance
    payments_total = Payment.objects.filter(invoice=invoice).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    remaining_balance = invoice.total_ttc - payments_total
    
    if remaining_balance <= 0:
        messages.info(request, 'Cette facture est déjà entièrement payée.')
        return redirect('invoices:detail', pk=invoice.pk)
    
    # Calculate quick amounts for template
    quick_amounts = {
        'amount_25': remaining_balance * Decimal('0.25'),
        'amount_50': remaining_balance * Decimal('0.50'),
        'amount_75': remaining_balance * Decimal('0.75'),
        'amount_100': remaining_balance,
    }
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.created_by = request.user
            
            # Validate payment amount
            if payment.amount > remaining_balance:
                messages.error(request, f'Le montant du paiement ({payment.amount} DA) ne peut pas dépasser le solde restant ({remaining_balance} DA).')
                return render(request, 'invoices/payment_form.html', {
                    'form': form,
                    'invoice': invoice,
                    'remaining_balance': remaining_balance,
                    'quick_amounts': quick_amounts,
                    'title': 'Ajouter un paiement'
                })
            
            payment.save()
            
            # Recalculate totals and update status
            new_total_paid = payments_total + payment.amount
            new_balance = invoice.total_ttc - new_total_paid
            
            if new_balance <= 0:
                invoice.status = 'paid'
                invoice.save()
                messages.success(request, f'Paiement de {payment.amount} DA enregistré avec succès. La facture est maintenant entièrement payée.')
            else:
                if invoice.status == 'draft':
                    invoice.status = 'sent'
                    invoice.save()
                messages.success(request, f'Paiement de {payment.amount} DA enregistré avec succès. Solde restant: {new_balance} DA.')
            
            return redirect('invoices:detail', pk=invoice.pk)
    else:
        form = PaymentForm(initial={
            'amount': remaining_balance,
            'payment_date': timezone.now().date(),
            'payment_method': invoice.payment_method
        })
    
    context = {
        'form': form,
        'invoice': invoice,
        'remaining_balance': remaining_balance,
        'quick_amounts': quick_amounts,
        'title': 'Ajouter un paiement'
    }
    return render(request, 'invoices/payment_form.html', context)

@login_required
def payment_delete(request, payment_pk):
    """Delete a payment"""
    payment = get_object_or_404(Payment, pk=payment_pk)
    invoice = payment.invoice
    
    # Check if user has permission to delete
    if request.user != payment.created_by and not request.user.is_superuser:
        messages.error(request, 'Vous n\'avez pas la permission de supprimer ce paiement.')
        return redirect('invoices:detail', pk=invoice.pk)
    
    if request.method == 'POST':
        payment_amount = payment.amount
        payment.delete()
        
        # Update invoice status after deletion
        remaining_payments = Payment.objects.filter(invoice=invoice)
        total_paid = remaining_payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        if total_paid < invoice.total_ttc:
            invoice.status = 'sent' if total_paid > 0 else 'draft'
            invoice.save()
        
        messages.success(request, f'Paiement de {payment_amount} DA supprimé avec succès.')
        return redirect('invoices:detail', pk=invoice.pk)
    
    context = {
        'payment': payment,
        'invoice': invoice,
        'title': 'Supprimer le paiement'
    }
    return render(request, 'invoices/payment_confirm_delete.html', context)

@login_required
def payment_history(request, invoice_pk):
    """View detailed payment history for an invoice"""
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    payments = Payment.objects.filter(invoice=invoice).order_by('-payment_date', '-created_at')
    
    # Pagination for large payment histories
    paginator = Paginator(payments, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    balance_due = invoice.total_ttc - total_paid
    
    context = {
        'invoice': invoice,
        'page_obj': page_obj,
        'total_paid': total_paid,
        'balance_due': balance_due,
        'title': f'Historique des paiements - {invoice.invoice_number}'
    }
    return render(request, 'invoices/payment_history.html', context)

@login_required
def payment_receipt(request, payment_pk):
    """Generate payment receipt"""
    payment = get_object_or_404(Payment, pk=payment_pk)
    company = Company.objects.first()
    
    context = {
        'payment': payment,
        'company': company,
        'title': f'Reçu de paiement - {payment.invoice.invoice_number}'
    }
    return render(request, 'invoices/payment_receipt.html', context)