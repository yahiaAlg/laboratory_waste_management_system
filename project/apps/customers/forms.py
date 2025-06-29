from django import forms
from django.forms import inlineformset_factory
from .models import Customer, ProductSubscription, SubscriptionUsage
from apps.inventory.models import Product

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'name', 'customer_type', 'address_line1', 'address_line2', 
            'city', 'postal_code', 'state', 'phone', 'fax', 'email',
            'activity', 'nis', 'rc', 'art', 'nif', 'credit_limit',
            'payment_terms', 'discount_rate', 'is_subscriber', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_type': forms.Select(attrs={'class': 'form-select'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'fax': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'activity': forms.TextInput(attrs={'class': 'form-control'}),
            'nis': forms.TextInput(attrs={'class': 'form-control'}),
            'rc': forms.TextInput(attrs={'class': 'form-control'}),
            'art': forms.TextInput(attrs={'class': 'form-control'}),
            'nif': forms.TextInput(attrs={'class': 'form-control'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_terms': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_subscriber': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProductSubscriptionForm(forms.ModelForm):
    class Meta:
        model = ProductSubscription
        fields = [
            'product', 'fixed_payment_amount', 'max_quantity_allowed',
            'billing_cycle', 'start_date', 'end_date', 'is_active'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'fixed_payment_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_quantity_allowed': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'billing_cycle': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active products
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        
        # Make product field required only if subscription data is provided
        if not any([
            self.data.get(f'{self.prefix}-product') if self.prefix else self.data.get('product'),
            self.data.get(f'{self.prefix}-fixed_payment_amount') if self.prefix else self.data.get('fixed_payment_amount'),
            self.data.get(f'{self.prefix}-max_quantity_allowed') if self.prefix else self.data.get('max_quantity_allowed')
        ]):
            self.fields['product'].required = False
            self.fields['fixed_payment_amount'].required = False
            self.fields['max_quantity_allowed'].required = False
            self.fields['start_date'].required = False

class SubscriptionUsageForm(forms.ModelForm):
    class Meta:
        model = SubscriptionUsage
        fields = ['quantity_used', 'usage_date', 'reference', 'notes']
        widgets = {
            'quantity_used': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'usage_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Inline formset for managing customer subscriptions
ProductSubscriptionFormSet = inlineformset_factory(
    Customer,
    ProductSubscription,
    form=ProductSubscriptionForm,
    extra=1,
    can_delete=True,
    fields=['product', 'fixed_payment_amount', 'max_quantity_allowed', 'billing_cycle', 'start_date', 'end_date', 'is_active']
)