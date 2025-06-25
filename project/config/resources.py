# project\config\resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django.contrib.auth import get_user_model

# Import all models
from apps.authentication.models import User
from apps.company.models import Company
from apps.customers.models import City, Customer
from apps.inventory.models import Category, Product, StockMovement
from apps.invoices.models import Invoice, InvoiceLine, Payment
from apps.suppliers.models import Supplier

User = get_user_model()


class UserResource(resources.ModelResource):
    role_display = fields.Field(attribute='get_role_display', readonly=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 
                 'phone', 'is_active', 'is_staff', 'date_joined', 'created_at', 'updated_at')
        export_order = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 
                       'phone', 'is_active', 'is_staff', 'date_joined')


class CityResource(resources.ModelResource):
    class Meta:
        model = City
        fields = ('id', 'name', 'code')
        export_order = ('id', 'name', 'code')


class CompanyResource(resources.ModelResource):
    state = fields.Field(
        column_name='state',
        attribute='state',
        widget=ForeignKeyWidget(City, 'name')
    )
    
    class Meta:
        model = Company
        fields = ('id', 'name', 'business_description', 'address_line1', 'address_line2', 
                 'city', 'postal_code', 'state', 'phone', 'fax', 'email', 'website',
                 'capital_social', 'rc', 'art', 'nis', 'nif', 'rib', 'tva_rate', 
                 'timbre_fiscal', 'invoice_prefix', 'next_invoice_number', 'created_at')
        export_order = ('id', 'name', 'business_description', 'address_line1', 'city', 
                       'postal_code', 'state', 'phone', 'email')


class CustomerResource(resources.ModelResource):
    state = fields.Field(
        column_name='state',
        attribute='state',
        widget=ForeignKeyWidget(City, 'name')
    )
    customer_type_display = fields.Field(attribute='get_customer_type_display', readonly=True)
    
    class Meta:
        model = Customer
        fields = ('id', 'name', 'customer_type', 'customer_type_display', 'address_line1', 
                 'address_line2', 'city', 'postal_code', 'state', 'phone', 'fax', 'email',
                 'activity', 'nis', 'rc', 'art', 'nif', 'credit_limit', 'payment_terms',
                 'discount_rate', 'is_active', 'created_at', 'updated_at')
        export_order = ('id', 'name', 'customer_type', 'customer_type_display', 'address_line1', 
                       'city', 'state', 'phone', 'email', 'is_active')


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'is_active')
        export_order = ('id', 'name', 'description', 'is_active')


class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    unit_display = fields.Field(attribute='get_unit_display', readonly=True)
    hazard_level_display = fields.Field(attribute='get_hazard_level_display', readonly=True)
    stock_status = fields.Field(attribute='stock_status', readonly=True)
    is_low_stock = fields.Field(attribute='is_low_stock', readonly=True)
    
    class Meta:
        model = Product
        fields = ('id', 'code', 'name', 'description', 'category', 'unit_price', 'unit', 
                 'unit_display', 'is_service', 'stock_quantity', 'minimum_stock', 
                 'hazard_level', 'hazard_level_display', 'storage_requirements', 
                 'handling_instructions', 'is_active', 'stock_status', 'is_low_stock',
                 'created_at', 'updated_at')
        export_order = ('id', 'code', 'name', 'category', 'unit_price', 'unit', 'stock_quantity', 
                       'minimum_stock', 'is_service', 'is_active')


class StockMovementResource(resources.ModelResource):
    product = fields.Field(
        column_name='product',
        attribute='product',
        widget=ForeignKeyWidget(Product, 'name')
    )
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'username')
    )
    movement_type_display = fields.Field(attribute='get_movement_type_display', readonly=True)
    
    class Meta:
        model = StockMovement
        fields = ('id', 'product', 'movement_type', 'movement_type_display', 'quantity', 
                 'reference', 'notes', 'date', 'created_by')
        export_order = ('id', 'product', 'movement_type', 'movement_type_display', 'quantity', 
                       'reference', 'date', 'created_by')


class InvoiceResource(resources.ModelResource):
    customer = fields.Field(
        column_name='customer',
        attribute='customer',
        widget=ForeignKeyWidget(Customer, 'name')
    )
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'username')
    )
    status_display = fields.Field(attribute='get_status_display', readonly=True)
    payment_method_display = fields.Field(attribute='get_payment_method_display', readonly=True)
    is_overdue = fields.Field(attribute='is_overdue', readonly=True)
    
    class Meta:
        model = Invoice
        fields = ('id', 'invoice_number', 'invoice_date', 'due_date', 'customer', 
                 'payment_method', 'payment_method_display', 'driver_name', 
                 'vehicle_registration', 'destination', 'subtotal_ht', 'tva_amount', 
                 'timbre_fiscal', 'other_taxes', 'discount_amount', 'total_ttc', 
                 'status', 'status_display', 'notes', 'is_overdue', 'created_at', 
                 'updated_at', 'created_by')
        export_order = ('id', 'invoice_number', 'invoice_date', 'due_date', 'customer', 
                       'status', 'total_ttc', 'payment_method', 'created_by')


class InvoiceLineResource(resources.ModelResource):
    invoice = fields.Field(
        column_name='invoice',
        attribute='invoice',
        widget=ForeignKeyWidget(Invoice, 'invoice_number')
    )
    product = fields.Field(
        column_name='product',
        attribute='product',
        widget=ForeignKeyWidget(Product, 'name')
    )
    
    class Meta:
        model = InvoiceLine
        fields = ('id', 'invoice', 'product', 'reference', 'description', 'unit', 
                 'quantity', 'unit_price', 'line_total')
        export_order = ('id', 'invoice', 'product', 'description', 'quantity', 
                       'unit_price', 'line_total')


class PaymentResource(resources.ModelResource):
    invoice = fields.Field(
        column_name='invoice',
        attribute='invoice',
        widget=ForeignKeyWidget(Invoice, 'invoice_number')
    )
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'username')
    )
    payment_method_display = fields.Field(attribute='get_payment_method_display', readonly=True)
    
    class Meta:
        model = Payment
        fields = ('id', 'invoice', 'amount', 'payment_date', 'payment_method', 
                 'payment_method_display', 'reference', 'notes', 'created_at', 'created_by')
        export_order = ('id', 'invoice', 'amount', 'payment_date', 'payment_method', 
                       'reference', 'created_by')


class SupplierResource(resources.ModelResource):
    state = fields.Field(
        column_name='state',
        attribute='state',
        widget=ForeignKeyWidget(City, 'name')
    )
    
    class Meta:
        model = Supplier
        fields = ('id', 'name', 'contact_person', 'address_line1', 'address_line2', 
                 'city', 'postal_code', 'state', 'phone', 'fax', 'email', 'website',
                 'services_provided', 'rc', 'nis', 'nif', 'payment_terms', 'rating',
                 'contract_start_date', 'contract_end_date', 'is_active', 'created_at', 
                 'updated_at')
        export_order = ('id', 'name', 'contact_person', 'address_line1', 'city', 'state', 
                       'phone', 'email', 'rating', 'is_active')