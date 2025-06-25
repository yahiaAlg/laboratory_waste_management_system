# Enhanced forms.py with improved payment form

from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Invoice, InvoiceLine, Payment

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'customer', 'invoice_date', 'due_date', 'payment_method',
            'driver_name', 'vehicle_registration', 'destination',
            'timbre_fiscal', 'other_taxes', 'discount_amount', 'notes'
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_registration': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'timbre_fiscal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_taxes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class InvoiceLineForm(forms.ModelForm):
    class Meta:
        model = InvoiceLine
        fields = ['product', 'reference', 'description', 'unit', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select product-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01'}),
        }

# Formset for invoice lines
InvoiceLineFormSet = inlineformset_factory(
    Invoice, InvoiceLine, form=InvoiceLineForm,
    extra=1, can_delete=True, can_delete_extra=True
)

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_date', 'payment_method', 'reference', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Montant du paiement'
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de chèque, référence de virement, etc.'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Notes additionnelles (optionnel)'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        self.invoice = kwargs.pop('invoice', None)
        super().__init__(*args, **kwargs)
        
        # Set payment method choices with French labels
        self.fields['payment_method'].choices = [
            ('', '--- Sélectionner ---'),
            ('cash', '💵 Espèces'),
            ('card', '💳 Carte bancaire'), 
            ('check', '📄 Chèque'),
            ('transfer', '🏦 Virement'),
        ]
        
        # Add help text
        self.fields['reference'].help_text = "Numéro de chèque, référence de virement, etc."
        
        if self.invoice:
            # Calculate remaining balance
            from django.db.models import Sum
            paid_amount = Payment.objects.filter(invoice=self.invoice).aggregate(
                Sum('amount'))['amount__sum'] or Decimal('0')
            remaining = self.invoice.total_ttc - paid_amount
            
            # Set max amount validation
            self.fields['amount'].widget.attrs['max'] = str(remaining)
            if remaining > 0:
                self.fields['amount'].widget.attrs['placeholder'] = f'Montant max: {remaining} DA'
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        if amount is None:
            raise ValidationError("Le montant est requis.")
            
        if amount <= 0:
            raise ValidationError("Le montant doit être supérieur à zéro.")
        
        if self.invoice:
            # Check if amount exceeds remaining balance
            from django.db.models import Sum
            paid_amount = Payment.objects.filter(invoice=self.invoice).aggregate(
                Sum('amount'))['amount__sum'] or Decimal('0')
            remaining = self.invoice.total_ttc - paid_amount
            
            if amount > remaining:
                raise ValidationError(
                    f"Le montant ({amount} DA) ne peut pas dépasser le solde restant ({remaining} DA)."
                )
        
        return amount
    
    def clean_reference(self):
        reference = self.cleaned_data.get('reference', '').strip()
        payment_method = self.cleaned_data.get('payment_method')
        
        # Require reference for checks and transfers
        if payment_method in ['check', 'transfer'] and not reference:
            if payment_method == 'check':
                raise ValidationError("Le numéro de chèque est requis.")
            else:
                raise ValidationError("La référence de virement est requise.")
        
        return reference

class QuickPaymentForm(forms.Form):
    """Quick payment form for common amounts"""
    QUICK_AMOUNTS = [
        ('25', '25%'),
        ('50', '50%'), 
        ('75', '75%'),
        ('100', '100%'),
        ('custom', 'Montant personnalisé'),
    ]
    
    amount_type = forms.ChoiceField(
        choices=QUICK_AMOUNTS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='100'
    )
    
    custom_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Montant personnalisé'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    reference = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Référence (optionnel)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.invoice = kwargs.pop('invoice', None)
        super().__init__(*args, **kwargs)
        
        if self.invoice:
            # Calculate remaining balance for percentage calculations
            from django.db.models import Sum
            paid_amount = Payment.objects.filter(invoice=self.invoice).aggregate(
                Sum('amount'))['amount__sum'] or Decimal('0')
            self.remaining_balance = self.invoice.total_ttc - paid_amount
    
    def clean(self):
        cleaned_data = super().clean()
        amount_type = cleaned_data.get('amount_type')
        custom_amount = cleaned_data.get('custom_amount')
        
        if amount_type == 'custom':
            if not custom_amount:
                raise ValidationError("Veuillez saisir un montant personnalisé.")
            if custom_amount > self.remaining_balance:
                raise ValidationError(f"Le montant ne peut pas dépasser {self.remaining_balance} DA.")
        
        return cleaned_data
    
    def get_payment_amount(self):
        """Calculate the actual payment amount based on selection"""
        amount_type = self.cleaned_data.get('amount_type')
        
        if amount_type == 'custom':
            return self.cleaned_data.get('custom_amount')
        else:
            percentage = Decimal(amount_type) / 100
            return self.remaining_balance * percentage