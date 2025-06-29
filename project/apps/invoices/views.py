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
from apps.customers.models import *


@login_required
def invoice_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    total_min = request.GET.get('total_min', '')
    total_max = request.GET.get('total_max', '')
    
    invoices = Invoice.objects.select_related('customer').all()
    
    # Text search
    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    # Status filter
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    # Date range filter
    if date_from:
        invoices = invoices.filter(invoice_date__gte=date_from)
    if date_to:
        invoices = invoices.filter(invoice_date__lte=date_to)
    
    # Total amount range filter
    if total_min:
        try:
            invoices = invoices.filter(total_ttc__gte=Decimal(total_min))
        except (ValueError, TypeError):
            pass
    if total_max:
        try:
            invoices = invoices.filter(total_ttc__lte=Decimal(total_max))
        except (ValueError, TypeError):
            pass
    
    paginator = Paginator(invoices, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate filter summary
    total_invoices = invoices.count()
    total_amount = invoices.aggregate(Sum('total_ttc'))['total_ttc__sum'] or Decimal('0')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_min': total_min,
        'total_max': total_max,
        'status_choices': Invoice.STATUS_CHOICES,
        'total_invoices': total_invoices,
        'total_amount': total_amount,
    }
    return render(request, 'invoices/invoice_list.html', context)


@login_required
def invoice_create(request):
    company = Company.objects.first()
    products = Product.objects.filter(is_active=True).order_by('code', 'name')
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceLineFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            
            formset.instance = invoice
            invoice_lines = formset.save()
            
            # Handle subscription usage tracking
            customer = invoice.customer
            if customer.has_active_subscriptions():
                for line in invoice_lines:
                    if line.product:
                        subscription = ProductSubscription.objects.filter(
                            customer=customer,
                            product=line.product,
                            is_active=True
                        ).first()
                        
                        if subscription:
                            # Track usage for subscribed products
                            SubscriptionUsage.objects.create(
                                subscription=subscription,
                                quantity_used=line.quantity,
                                usage_date=invoice.invoice_date,
                                reference=f"Facture {invoice.invoice_number}",
                                created_by=request.user
                            )
            
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
        'products': products,
        'title': 'Créer une facture'
    }
    return render(request, 'invoices/invoice_form.html', context)

@login_required
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    company = Company.objects.first()
    products = Product.objects.filter(is_active=True).order_by('code', 'name')
    
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
        'products': products,
        'title': 'Modifier la facture'
    }
    return render(request, 'invoices/invoice_form.html', context)


@login_required
def invoice_delete(request, pk):
    """Delete an invoice - only for admin users"""
    if request.user.role != 'admin':
        messages.error(request, 'Seuls les administrateurs peuvent supprimer les factures.')
        return redirect('invoices:detail', pk=pk)
    
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Check if invoice has payments
    has_payments = Payment.objects.filter(invoice=invoice).exists()
    
    if has_payments:
        messages.error(request, 'Impossible de supprimer une facture avec des paiements enregistrés.')
        return redirect('invoices:detail', pk=invoice.pk)
    
    if request.method == 'POST':
        invoice_number = invoice.invoice_number
        customer_name = invoice.customer.name
        
        # Delete related subscription usage records
        if hasattr(invoice.customer, 'subscriptions'):
            from apps.customers.models import SubscriptionUsage
            SubscriptionUsage.objects.filter(
                reference__icontains=invoice.invoice_number
            ).delete()
        
        invoice.delete()
        
        messages.success(request, f'Facture {invoice_number} de {customer_name} supprimée avec succès.')
        return redirect('invoices:list')
    
    context = {
        'invoice': invoice,
        'has_payments': has_payments,
        'title': 'Supprimer la facture'
    }
    return render(request, 'invoices/invoice_confirm_delete.html', context)

@login_required
def get_customer_legal_info(request):
    """AJAX view to check if customer has legal information"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    customer_id = request.GET.get('customer_id')
    
    if not customer_id:
        return JsonResponse({'has_legal_info': False})
    
    try:
        customer_id = int(customer_id)
        customer = Customer.objects.get(pk=customer_id)
        
        # Check if customer has required legal information
        has_legal_info = bool(
            customer.nis or 
            customer.rc or 
            customer.art or
            customer.nif
        )
        
        return JsonResponse({
            'has_legal_info': has_legal_info,
            'customer_id': customer.id,
            'customer_name': customer.name
        })
        
    except (ValueError, Customer.DoesNotExist):
        return JsonResponse({'has_legal_info': False})
    except Exception as e:
        return JsonResponse({'error': 'Server error occurred'}, status=500)


@login_required
def get_customer_subscriptions(request):
    """AJAX view to get customer's active subscriptions"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    customer_id = request.GET.get('customer_id')
    
    if not customer_id:
        return JsonResponse({'subscriptions': []})
    
    try:
        customer_id = int(customer_id)
        customer = Customer.objects.get(pk=customer_id)
        
        subscriptions = ProductSubscription.objects.filter(
            customer=customer,
            is_active=True
        ).select_related('product')
        
        subscription_data = []
        for sub in subscriptions:
            subscription_data.append({
                'product_id': sub.product.id,
                'product_name': sub.product.name,
                'product_code': sub.product.code,
                'fixed_payment_amount': str(sub.fixed_payment_amount),
                'remaining_quantity': str(sub.remaining_quantity),
                'max_quantity': str(sub.max_quantity_allowed),
                'billing_cycle': sub.get_billing_cycle_display(),
            })
        
        return JsonResponse({
            'subscriptions': subscription_data,
            'has_subscriptions': len(subscription_data) > 0,
            'is_subscriber': customer.is_subscriber
        })
        
    except (ValueError, Customer.DoesNotExist):
        return JsonResponse({'subscriptions': []})
    except Exception as e:
        return JsonResponse({'error': 'Server error occurred'}, status=500)

@login_required
def get_product_data(request):
    """AJAX view to get product data for invoice lines"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    product_id = request.GET.get('product_id')
    customer_id = request.GET.get('customer_id')
    
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
            'is_subscribed': False,
            'subscription_price': None,
            'remaining_quantity': None,
        }
        
        # Check if customer has subscription for this product
        if customer_id:
            try:
                customer_id = int(customer_id)
                subscription = ProductSubscription.objects.filter(
                    customer_id=customer_id,
                    product=product,
                    is_active=True
                ).first()
                
                if subscription:
                    data.update({
                        'is_subscribed': True,
                        'subscription_price': str(subscription.fixed_payment_amount),
                        'remaining_quantity': str(subscription.remaining_quantity),
                        'max_quantity': str(subscription.max_quantity_allowed),
                    })
            except (ValueError, TypeError):
                pass
        
        return JsonResponse(data)
        
    except ValueError:
        return JsonResponse({'error': 'Invalid product ID format'}, status=400)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Server error occurred'}, status=500)

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
    
    # Get customer subscription information
    customer_subscriptions = []
    subscription_summary = {
        'total_subscribed_amount': Decimal('0'),
        'total_used_this_period': Decimal('0'),
        'total_remaining_quantity': Decimal('0'),
        'has_subscriptions': False
    }
    
    if invoice.customer.is_subscriber:
        # Get active subscriptions for this customer
        active_subscriptions = ProductSubscription.objects.filter(
            customer=invoice.customer,
            is_active=True
        ).select_related('product')
        
        if active_subscriptions.exists():
            subscription_summary['has_subscriptions'] = True
            
            for subscription in active_subscriptions:
                # Calculate usage for current billing period
                from django.utils import timezone
                today = timezone.now().date()
                
                # Determine period start based on billing cycle
                if subscription.billing_cycle == 'monthly':
                    period_start = today.replace(day=1)
                elif subscription.billing_cycle == 'quarterly':
                    quarter = (today.month - 1) // 3
                    period_start = today.replace(month=quarter * 3 + 1, day=1)
                else:  # yearly
                    period_start = today.replace(month=1, day=1)
                
                # Get usage in current period
                current_usage = SubscriptionUsage.objects.filter(
                    subscription=subscription,
                    usage_date__gte=period_start,
                    usage_date__lte=today
                ).aggregate(
                    total_used=Sum('quantity_used')
                )['total_used'] or Decimal('0')
                
                remaining_qty = subscription.max_quantity_allowed - current_usage
                
                # Check if any invoice lines match this subscription product
                invoice_lines_for_product = invoice.invoiceline_set.filter(
                    product=subscription.product
                )
                
                subscription_data = {
                    'subscription': subscription,
                    'current_usage': current_usage,
                    'remaining_quantity': max(Decimal('0'), remaining_qty),
                    'period_start': period_start,
                    'invoice_lines': invoice_lines_for_product,
                    'is_over_limit': current_usage > subscription.max_quantity_allowed,
                    'usage_percentage': (current_usage / subscription.max_quantity_allowed * 100) if subscription.max_quantity_allowed > 0 else 0
                }
                
                customer_subscriptions.append(subscription_data)
                
                # Update summary
                subscription_summary['total_subscribed_amount'] += subscription.fixed_payment_amount
                subscription_summary['total_used_this_period'] += current_usage
                subscription_summary['total_remaining_quantity'] += subscription_data['remaining_quantity']
    
    # Get recent subscription usage related to this invoice
    invoice_related_usage = []
    if invoice.customer.is_subscriber:
        invoice_related_usage = SubscriptionUsage.objects.filter(
            subscription__customer=invoice.customer,
            reference__icontains=invoice.invoice_number
        ).select_related('subscription', 'subscription__product').order_by('-usage_date')
    
    context = {
        'invoice': invoice,
        'payments': payments,
        'total_paid': total_paid,
        'balance_due': balance_due,
        'payments_count': payments.count(),
        'customer_subscriptions': customer_subscriptions,
        'subscription_summary': subscription_summary,
        'invoice_related_usage': invoice_related_usage,
    }
    return render(request, 'invoices/invoice_detail.html', context)

# Rest of the payment-related views remain the same...
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