from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Prefetch
from django.http import JsonResponse
from django.forms import ValidationError
from .models import Customer, ProductSubscription
from .forms import CustomerForm, ProductSubscriptionFormSet, SubscriptionUsageForm

@login_required
def customer_list(request):
    # Get all filter parameters
    search_query = request.GET.get('search', '')
    customer_type = request.GET.get('customer_type', '')
    subscription_status = request.GET.get('subscription_status', '')
    status = request.GET.get('status', '')
    city = request.GET.get('city', '')
    payment_terms = request.GET.get('payment_terms', '')
    credit_limit_min = request.GET.get('credit_limit_min', '')
    credit_limit_max = request.GET.get('credit_limit_max', '')
    discount_rate_min = request.GET.get('discount_rate_min', '')
    discount_rate_max = request.GET.get('discount_rate_max', '')
    
    # Start with all customers and prefetch subscription data
    customers = Customer.objects.prefetch_related(
        Prefetch('subscriptions', queryset=ProductSubscription.objects.filter(is_active=True))
    ).annotate(
        total_subscription_amount=Sum('subscriptions__fixed_payment_amount', 
                                    filter=Q(subscriptions__is_active=True))
    )
    
    # Apply text search (enhanced to include more fields)
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(address_line1__icontains=search_query) |
            Q(address_line2__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(activity__icontains=search_query)
        )
    
    # Apply customer type filter
    if customer_type:
        customers = customers.filter(customer_type=customer_type)
    
    # Apply subscription status filter
    if subscription_status == 'subscriber':
        customers = customers.filter(is_subscriber=True)
    elif subscription_status == 'non_subscriber':
        customers = customers.filter(is_subscriber=False)
    elif subscription_status == 'has_active_subscriptions':
        customers = customers.filter(subscriptions__is_active=True).distinct()
    elif subscription_status == 'no_active_subscriptions':
        customers = customers.exclude(subscriptions__is_active=True)
    
    # Apply active status filter
    if status == 'active':
        customers = customers.filter(is_active=True)
    elif status == 'inactive':
        customers = customers.filter(is_active=False)
    
    # Apply city filter
    if city:
        customers = customers.filter(city__icontains=city)
    
    # Apply payment terms filter
    if payment_terms:
        customers = customers.filter(payment_terms=payment_terms)
    
    # Apply credit limit range filter
    if credit_limit_min:
        try:
            customers = customers.filter(credit_limit__gte=float(credit_limit_min))
        except ValueError:
            pass
    
    if credit_limit_max:
        try:
            customers = customers.filter(credit_limit__lte=float(credit_limit_max))
        except ValueError:
            pass
    
    # Apply discount rate range filter
    if discount_rate_min:
        try:
            customers = customers.filter(discount_rate__gte=float(discount_rate_min))
        except ValueError:
            pass
    
    if discount_rate_max:
        try:
            customers = customers.filter(discount_rate__lte=float(discount_rate_max))
        except ValueError:
            pass
    
    # Order results
    customers = customers.order_by('name')
    
    # Pagination
    paginator = Paginator(customers, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Prepare context with all filter values for template
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'customer_type': customer_type,
        'subscription_status': subscription_status,
        'status': status,
        'city': city,
        'payment_terms': payment_terms,
        'credit_limit_min': credit_limit_min,
        'credit_limit_max': credit_limit_max,
        'discount_rate_min': discount_rate_min,
        'discount_rate_max': discount_rate_max,
    }
    return render(request, 'customers/customer_list.html', context)

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    # Get active subscriptions with usage data
    active_subscriptions = customer.subscriptions.filter(is_active=True).select_related('product')
    
    # Get recent usage for each subscription
    subscription_data = []
    for subscription in active_subscriptions:
        recent_usage = subscription.usages.order_by('-usage_date')[:5]
        subscription_data.append({
            'subscription': subscription,
            'remaining_quantity': subscription.remaining_quantity,
            'recent_usage': recent_usage
        })
    
    context = {
        'customer': customer,
        'subscription_data': subscription_data,
        'total_subscription_amount': customer.get_total_subscription_amount()
    }
    return render(request, 'customers/customer_detail.html', context)

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        formset = ProductSubscriptionFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            customer = form.save()
            
            # Save subscriptions if customer is marked as subscriber
            if customer.is_subscriber:
                formset.instance = customer
                formset.save()
                
                subscription_count = len([f for f in formset if f.cleaned_data and not f.cleaned_data.get('DELETE')])
                if subscription_count > 0:
                    messages.success(request, f'Client {customer.name} créé avec {subscription_count} abonnement(s).')
                else:
                    messages.success(request, f'Client {customer.name} créé avec succès.')
            else:
                messages.success(request, f'Client {customer.name} créé avec succès.')
            
            return redirect('customers:detail', pk=customer.pk)
    else:
        form = CustomerForm()
        formset = ProductSubscriptionFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Ajouter un client'
    }
    return render(request, 'customers/customer_form.html', context)

@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        formset = ProductSubscriptionFormSet(request.POST, instance=customer)
        
        if form.is_valid() and formset.is_valid():
            customer = form.save()
            
            # Handle subscriptions based on is_subscriber status
            if customer.is_subscriber:
                formset.save()
                messages.success(request, f'Client {customer.name} et ses abonnements modifiés avec succès.')
            else:
                # If no longer subscriber, deactivate all subscriptions
                customer.subscriptions.update(is_active=False)
                messages.success(request, f'Client {customer.name} modifié avec succès. Abonnements désactivés.')
            
            return redirect('customers:detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
        formset = ProductSubscriptionFormSet(instance=customer)
    
    context = {
        'form': form,
        'formset': formset,
        'customer': customer,
        'title': 'Modifier le client'
    }
    return render(request, 'customers/customer_form.html', context)

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer_name = customer.name
        customer.delete()
        messages.success(request, f'Client {customer_name} supprimé avec succès.')
        return redirect('customers:list')
    
    context = {'customer': customer}
    return render(request, 'customers/customer_confirm_delete.html', context)

@login_required
def subscription_usage_create(request, subscription_id):
    """Create usage record for a subscription"""
    subscription = get_object_or_404(ProductSubscription, pk=subscription_id, is_active=True)
    
    if request.method == 'POST':
        form = SubscriptionUsageForm(request.POST)
        if form.is_valid():
            usage = form.save(commit=False)
            usage.subscription = subscription
            usage.created_by = request.user
            
            try:
                usage.full_clean()  # This will call the clean method
                usage.save()
                messages.success(request, f'Utilisation enregistrée pour {subscription.product.name}.')
                return redirect('customers:detail', pk=subscription.customer.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = SubscriptionUsageForm()
    
    context = {
        'form': form,
        'subscription': subscription,
        'remaining_quantity': subscription.remaining_quantity,
        'title': f'Enregistrer utilisation - {subscription.product.name}'
    }
    return render(request, 'customers/subscription_usage_form.html', context)

@login_required
def subscription_usage_list(request, subscription_id):
    """List all usage records for a subscription"""
    subscription = get_object_or_404(ProductSubscription, pk=subscription_id)
    usage_list = subscription.usages.order_by('-usage_date')
    
    # Pagination
    paginator = Paginator(usage_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'subscription': subscription,
        'page_obj': page_obj,
        'remaining_quantity': subscription.remaining_quantity
    }
    return render(request, 'customers/subscription_usage_list.html', context)

@login_required
def subscription_detail(request, pk):
    """Detailed view of a specific subscription"""
    subscription = get_object_or_404(ProductSubscription, pk=pk)
    recent_usage = subscription.usages.order_by('-usage_date')[:10]
    
    # Calculate usage statistics
    from django.utils import timezone
    from dateutil.relativedelta import relativedelta
    
    today = timezone.now().date()
    if subscription.billing_cycle == 'monthly':
        period_start = today.replace(day=1)
    elif subscription.billing_cycle == 'quarterly':
        quarter = (today.month - 1) // 3
        period_start = today.replace(month=quarter * 3 + 1, day=1)
    else:  # yearly
        period_start = today.replace(month=1, day=1)
    
    current_period_usage = subscription.usages.filter(
        usage_date__gte=period_start,
        usage_date__lte=today
    ).aggregate(total=Sum('quantity_used'))['total'] or 0
    
    context = {
        'subscription': subscription,
        'recent_usage': recent_usage,
        'current_period_usage': current_period_usage,
        'remaining_quantity': subscription.remaining_quantity,
        'period_start': period_start
    }
    return render(request, 'customers/subscription_detail.html', context)

# AJAX endpoint for subscription management
@login_required
def get_subscription_info(request, subscription_id):
    """AJAX endpoint to get subscription info"""
    try:
        subscription = ProductSubscription.objects.get(pk=subscription_id, is_active=True)
        data = {
            'product_name': subscription.product.name,
            'fixed_amount': float(subscription.fixed_payment_amount),
            'max_quantity': float(subscription.max_quantity_allowed),
            'remaining_quantity': float(subscription.remaining_quantity),
            'billing_cycle': subscription.get_billing_cycle_display()
        }
        return JsonResponse(data)
    except ProductSubscription.DoesNotExist:
        return JsonResponse({'error': 'Subscription not found'}, status=404)