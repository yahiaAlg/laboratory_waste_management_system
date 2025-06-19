from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Supplier
from .forms import SupplierForm

@login_required
def supplier_list(request):
    search_query = request.GET.get('search', '')
    suppliers = Supplier.objects.all()
    
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    paginator = Paginator(suppliers, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'suppliers/supplier_list.html', context)

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    context = {'supplier': supplier}
    return render(request, 'suppliers/supplier_detail.html', context)

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Fournisseur {supplier.name} créé avec succès.')
            return redirect('suppliers:detail', pk=supplier.pk)
    else:
        form = SupplierForm()
    
    context = {'form': form, 'title': 'Ajouter un fournisseur'}
    return render(request, 'suppliers/supplier_form.html', context)

@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Fournisseur {supplier.name} modifié avec succès.')
            return redirect('suppliers:detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)
    
    context = {'form': form, 'supplier': supplier, 'title': 'Modifier le fournisseur'}
    return render(request, 'suppliers/supplier_form.html', context)

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        supplier_name = supplier.name
        supplier.delete()
        messages.success(request, f'Fournisseur {supplier_name} supprimé avec succès.')
        return redirect('suppliers:list')
    
    context = {'supplier': supplier}
    return render(request, 'suppliers/supplier_confirm_delete.html', context)