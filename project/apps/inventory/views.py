from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import models
from .models import Product, Category, StockMovement
from .forms import ProductForm, StockMovementForm

@login_required
def product_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    products = Product.objects.select_related('category').all()
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'categories': categories,
        'category_filter': category_filter,
    }
    return render(request, 'inventory/product_list.html', context)

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
            messages.success(request, f'Produit/Service {product.name} créé avec succès.')
            return redirect('inventory:product_detail', pk=product.pk)
    else:
        form = ProductForm()
    
    context = {'form': form, 'title': 'Ajouter un produit/service'}
    return render(request, 'inventory/product_form.html', context)

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Produit/Service {product.name} modifié avec succès.')
            return redirect('inventory:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    context = {'form': form, 'product': product, 'title': 'Modifier le produit/service'}
    return render(request, 'inventory/product_form.html', context)

@login_required
def stock_movement_create(request, product_pk=None):
    product = None
    if product_pk:
        product = get_object_or_404(Product, pk=product_pk)
    
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.created_by = request.user
            movement.save()
            
            # Update stock quantity
            if movement.movement_type == 'in':
                movement.product.stock_quantity += movement.quantity
            elif movement.movement_type == 'out':
                movement.product.stock_quantity -= movement.quantity
            elif movement.movement_type == 'adjustment':
                movement.product.stock_quantity = movement.quantity
            
            movement.product.save()
            
            messages.success(request, 'Mouvement de stock enregistré avec succès.')
            return redirect('inventory:product_detail', pk=movement.product.pk)
    else:
        initial_data = {}
        if product:
            initial_data['product'] = product
        form = StockMovementForm(initial=initial_data)
    
    context = {'form': form, 'product': product, 'title': 'Ajouter un mouvement de stock'}
    return render(request, 'inventory/stock_movement_form.html', context)

@login_required
def low_stock_report(request):
    low_stock_products = Product.objects.filter(
        is_service=False,
        stock_quantity__lte=models.F('minimum_stock'),
        is_active=True
    ).select_related('category')
    
    context = {'low_stock_products': low_stock_products}
    return render(request, 'inventory/low_stock_report.html', context)