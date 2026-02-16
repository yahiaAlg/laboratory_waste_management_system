# Views Documentation

This document contains all Django views organized by application.

---

## Authentication App

```python
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, CustomPasswordChangeForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = UserLoginForm()

    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)

    return render(request, 'authentication/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('authentication:login')

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('authentication:login')

    def form_valid(self, form):
        messages.success(self.request, 'Compte créé avec succès. Vous pouvez maintenant vous connecter.')
        return super().form_valid(form)

@login_required
def profile_view(request):
    return render(request, 'authentication/profile.html')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('authentication:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'authentication/edit_profile.html', {'form': form})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Votre mot de passe a été changé avec succès.')
            return redirect('authentication:profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'authentication/change_password.html', {'form': form})
```

---

## Company App

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Company
from .forms import CompanyForm

@login_required
def company_settings(request):
    try:
        company = Company.objects.first()
        if not company:
            company = Company.objects.create(name="Ma Société")
    except Company.DoesNotExist:
        company = Company.objects.create(name="Ma Société")

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            company = form.save()
            messages.success(request, 'Informations de l\'entreprise mises à jour avec succès.')
            return redirect('company:settings')
    else:
        form = CompanyForm(instance=company)

    context = {'form': form, 'company': company}
    return render(request, 'company/settings.html', context)
```

---

## Customers App

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Prefetch, Count
from django.http import JsonResponse
from django.forms import ValidationError
from .models import Customer, ProductSubscription, SubscriptionUsage
from .forms import CustomerForm, ProductSubscriptionFormSet, SubscriptionUsageForm
# Calculate usage statistics
from django.utils import timezone

from datetime import timedelta
from apps.invoices.models import Invoice
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

# Replace the problematic lines in your customer_create view (around line 166)

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
                subscriptions = formset.save()

                # Count actual saved subscriptions (exclude deleted ones)
                subscription_count = len([s for s in subscriptions if s and hasattr(s, 'pk') and s.pk])

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
                # Save the formset - this will handle creation, updates, and deletions
                formset.save()
                messages.success(request, f'Client {customer.name} et ses abonnements modifiés avec succès.')
            else:
                # If no longer subscriber, deactivate all subscriptions instead of deleting them
                # This preserves historical data
                customer.subscriptions.update(is_active=False)
                messages.success(request, f'Client {customer.name} modifié avec succès. Abonnements désactivés.')

            return redirect('customers:detail', pk=customer.pk)
        else:
            # Add debugging information for form errors
            if not form.is_valid():
                messages.error(request, 'Erreurs dans le formulaire client.')
            if not formset.is_valid():
                messages.error(request, 'Erreurs dans les abonnements.')
                # Add specific formset errors to messages
                for i, form_errors in enumerate(formset.errors):
                    if form_errors:
                        for field, errors in form_errors.items():
                            messages.error(request, f'Abonnement {i+1}, {field}: {errors[0]}')

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





@login_required
def customer_statistics(request, pk):
    """Display comprehensive statistics for a specific customer"""
    customer = get_object_or_404(Customer, pk=pk)

    # Date range for statistics (last 12 months)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)

    # Basic customer stats
    total_invoices = Invoice.objects.filter(customer=customer).count()
    total_revenue = Invoice.objects.filter(customer=customer, status='paid').aggregate(
        total=Sum('total_ttc')
    )['total'] or 0

    pending_invoices = Invoice.objects.filter(
        customer=customer,
        status__in=['sent', 'overdue']
    ).count()

    overdue_invoices = Invoice.objects.filter(
        customer=customer,
        status='overdue'
    ).count()

    # Subscription statistics
    active_subscriptions = customer.subscriptions.filter(is_active=True)
    total_subscription_value = active_subscriptions.aggregate(
        total=Sum('fixed_payment_amount')
    )['total'] or 0

    # Monthly revenue data (last 12 months)
    monthly_revenue = []
    monthly_labels = []

    for i in range(12):
        month_start = (end_date.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        revenue = Invoice.objects.filter(
            customer=customer,
            invoice_date__gte=month_start,
            invoice_date__lte=month_end,
            status='paid'
        ).aggregate(total=Sum('total_ttc'))['total'] or 0

        monthly_revenue.insert(0, float(revenue))
        monthly_labels.insert(0, month_start.strftime('%b %Y'))

    # Invoice status distribution
    invoice_status_data = Invoice.objects.filter(customer=customer).values('status').annotate(
        count=Count('id')
    ).order_by('status')

    status_labels = []
    status_counts = []
    status_colors = {
        'draft': '#6c757d',
        'sent': '#0d6efd',
        'paid': '#198754',
        'overdue': '#dc3545',
        'cancelled': '#6f42c1'
    }

    for item in invoice_status_data:
        status_labels.append(item['status'].title())
        status_counts.append(item['count'])

    # Subscription usage data (last 6 months)
    subscription_usage_data = []
    usage_labels = []

    for subscription in active_subscriptions:
        monthly_usage = []

        for i in range(6):
            month_start = (end_date.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            usage = SubscriptionUsage.objects.filter(
                subscription=subscription,
                usage_date__gte=month_start,
                usage_date__lte=month_end
            ).aggregate(total=Sum('quantity_used'))['total'] or 0

            monthly_usage.insert(0, float(usage))

            if i == 0:  # Only create labels once
                usage_labels.insert(0, month_start.strftime('%b %Y'))

        subscription_usage_data.append({
            'label': subscription.product.name,
            'data': monthly_usage,
            'borderColor': f'rgb({hash(subscription.product.name) % 255}, {(hash(subscription.product.name) * 2) % 255}, {(hash(subscription.product.name) * 3) % 255})',
            'backgroundColor': f'rgba({hash(subscription.product.name) % 255}, {(hash(subscription.product.name) * 2) % 255}, {(hash(subscription.product.name) * 3) % 255}, 0.2)'
        })

    # Payment method distribution
    payment_methods = Invoice.objects.filter(customer=customer, status='paid').values('payment_method').annotate(
        count=Count('id')
    ).order_by('payment_method')

    payment_labels = []
    payment_counts = []
    payment_colors = ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0']

    for item in payment_methods:
        payment_labels.append(dict(Invoice.PAYMENT_METHOD_CHOICES)[item['payment_method']])
        payment_counts.append(item['count'])

    # Recent subscription usage summary
    recent_usage = SubscriptionUsage.objects.filter(
        subscription__customer=customer,
        usage_date__gte=start_date
    ).select_related('subscription__product').order_by('-usage_date')[:10]

    # Calculate subscription efficiency (usage vs. allowance)
    subscription_efficiency = []
    for subscription in active_subscriptions:
        # Calculate usage for current billing period
        today = timezone.now().date()
        if subscription.billing_cycle == 'monthly':
            period_start = today.replace(day=1)
        elif subscription.billing_cycle == 'quarterly':
            quarter = (today.month - 1) // 3
            period_start = today.replace(month=quarter * 3 + 1, day=1)
        else:  # yearly
            period_start = today.replace(month=1, day=1)

        current_usage = SubscriptionUsage.objects.filter(
            subscription=subscription,
            usage_date__gte=period_start,
            usage_date__lte=today
        ).aggregate(total=Sum('quantity_used'))['total'] or 0

        efficiency = (current_usage / subscription.max_quantity_allowed * 100) if subscription.max_quantity_allowed > 0 else 0

        subscription_efficiency.append({
            'product': subscription.product.name,
            'usage': float(current_usage),
            'allowance': float(subscription.max_quantity_allowed),
            'efficiency': round(efficiency, 2),
            'remaining': float(subscription.remaining_quantity)
        })

    context = {
        'customer': customer,
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
        'pending_invoices': pending_invoices,
        'overdue_invoices': overdue_invoices,
        'active_subscriptions_count': active_subscriptions.count(),
        'total_subscription_value': total_subscription_value,
        'monthly_revenue': monthly_revenue,
        'monthly_labels': monthly_labels,
        'status_labels': status_labels,
        'status_counts': status_counts,
        'payment_labels': payment_labels,
        'payment_counts': payment_counts,
        'subscription_usage_data': subscription_usage_data,
        'usage_labels': usage_labels,
        'recent_usage': recent_usage,
        'subscription_efficiency': subscription_efficiency,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'customers/customer_statistics.html', context)
```

---

## Dashboard App

```python
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
```

---

## Inventory App

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import models
from .models import Product, Category, StockMovement
from .forms import ProductForm, StockMovementForm

# Modify the product_list view to handle advanced filters:

@login_required
def product_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    # Advanced filters
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    stock_min = request.GET.get('stock_min', '')
    stock_max = request.GET.get('stock_max', '')
    is_service_filter = request.GET.get('is_service', '')
    is_active_filter = request.GET.get('is_active', '')

    products = Product.objects.select_related('category').all()

    # Text search (name and code)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query)
        )

    # Category filter
    if category_filter:
        products = products.filter(category_id=category_filter)

    # Price range filter
    if price_min:
        try:
            products = products.filter(unit_price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(unit_price__lte=float(price_max))
        except ValueError:
            pass

    # Stock range filter
    if stock_min:
        try:
            products = products.filter(stock_quantity__gte=float(stock_min))
        except ValueError:
            pass
    if stock_max:
        try:
            products = products.filter(stock_quantity__lte=float(stock_max))
        except ValueError:
            pass

    # Service/Product filter
    if is_service_filter == 'true':
        products = products.filter(is_service=True)
    elif is_service_filter == 'false':
        products = products.filter(is_service=False)

    # Active status filter
    if is_active_filter == 'true':
        products = products.filter(is_active=True)
    elif is_active_filter == 'false':
        products = products.filter(is_active=False)

    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'categories': categories,
        'category_filter': category_filter,
        # Advanced filter values for preserving form state
        'price_min': price_min,
        'price_max': price_max,
        'stock_min': stock_min,
        'stock_max': stock_max,
        'is_service_filter': is_service_filter,
        'is_active_filter': is_active_filter,
    }
    return render(request, 'inventory/product_list.html', context)


# Add this new view for product deletion:

@login_required
def product_delete(request, pk):
    # Only allow superusers to delete products
    if not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas les permissions pour supprimer des produits.")
        return redirect('inventory:product_list')

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product_name = product.name

        # Check if product has stock movements
        if StockMovement.objects.filter(product=product).exists():
            messages.warning(request,
                f"Le produit '{product_name}' a des mouvements de stock associés. "
                "Il a été désactivé au lieu d'être supprimé.")
            product.is_active = False
            product.save()
        else:
            product.delete()
            messages.success(request, f"Le produit '{product_name}' a été supprimé avec succès.")

        return redirect('inventory:product_list')

    return redirect('inventory:product_list')

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    recent_movements = StockMovement.objects.filter(product=product)[:10]

    context = {
        'product': product,
        'recent_movements': recent_movements,
    }
    return render(request, 'inventory/product_detail.html', context)

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
```
