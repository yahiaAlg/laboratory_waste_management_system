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