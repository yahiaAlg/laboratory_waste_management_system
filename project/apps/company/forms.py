from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'business_description', 'address_line1', 'address_line2',
            'city', 'postal_code', 'state', 'phone', 'fax', 'email', 'website',
            'capital_social', 'rc', 'art', 'nis', 'nif', 'rib', 'logo',
            'tva_rate', 'timbre_fiscal', 'invoice_prefix'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_description': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'fax': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'capital_social': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rc': forms.TextInput(attrs={'class': 'form-control'}),
            'art': forms.TextInput(attrs={'class': 'form-control'}),
            'nis': forms.TextInput(attrs={'class': 'form-control'}),
            'nif': forms.TextInput(attrs={'class': 'form-control'}),
            'rib': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'tva_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'timbre_fiscal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'invoice_prefix': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
        }