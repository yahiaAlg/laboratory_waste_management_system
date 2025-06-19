import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import transaction
from decimal import Decimal
import random
from datetime import timedelta, date

# Ensure Django is configured
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

# Import your models
from apps.authentication.models import User
from apps.company.models import Company
from apps.customers.models import City, Customer
from apps.inventory.models import Category, Product, StockMovement
from apps.invoices.models import Invoice, InvoiceLine, Payment
from apps.suppliers.models import Supplier

class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))
        
        # First, make sure cities are populated
        self.stdout.write('Ensuring cities are populated...')
        from django.core.management import call_command
        call_command('populate_cities')
        
        # Clear existing data (optional - comment out if you don't want to clear existing data)
        self.clear_data()
        
        # Create users with different roles
        users = self.create_users()
        
        # Create company profile
        company = self.create_company()
        
        # Create categories and products
        categories = self.create_categories()
        products = self.create_products(categories)
        
        # Create customers
        customers = self.create_customers()
        
        # Create suppliers
        suppliers = self.create_suppliers()
        
        # Create stock movements
        self.create_stock_movements(products, users)
        
        # Create invoices and payments
        self.create_invoices_and_payments(company, customers, products, users)
        
        self.stdout.write(self.style.SUCCESS('Database successfully populated!'))
        
    def clear_data(self):
        self.stdout.write('Clearing existing data...')
        Payment.objects.all().delete()
        InvoiceLine.objects.all().delete()
        Invoice.objects.all().delete()
        StockMovement.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Customer.objects.all().delete()
        Supplier.objects.all().delete()
        Company.objects.all().delete()
        # Don't delete all users to avoid removing the superuser
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('Existing data cleared!'))

    def create_users(self):
        self.stdout.write('Creating users...')
        
        # Create one user for each role
        users_data = [
            {
                'username': 'admin_user',
                'email': 'admin@example.com',
                'password': make_password('password123'),
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'phone': '+213555123456',
            },
            {
                'username': 'manager_user',
                'email': 'manager@example.com',
                'password': make_password('password123'),
                'first_name': 'Manager',
                'last_name': 'User',
                'role': 'manager',
                'phone': '+213555123457',
            },
            {
                'username': 'operator_user',
                'email': 'operator@example.com',
                'password': make_password('password123'),
                'first_name': 'Operator',
                'last_name': 'User',
                'role': 'operator',
                'phone': '+213555123458',
            },
            {
                'username': 'accountant_user',
                'email': 'accountant@example.com',
                'password': make_password('password123'),
                'first_name': 'Accountant',
                'last_name': 'User',
                'role': 'accountant',
                'phone': '+213555123459',
            },
            {
                'username': 'client_user',
                'email': 'client@example.com',
                'password': make_password('password123'),
                'first_name': 'Client',
                'last_name': 'User',
                'role': 'client',
                'phone': '+213555123460',
            },
        ]
        
        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                created_users.append(user)
                self.stdout.write(f'  Created user: {user.username} ({user.get_role_display()})')
            else:
                self.stdout.write(f'  User already exists: {user.username}')
                created_users.append(user)
        
        return created_users

    def create_company(self):
        self.stdout.write('Creating company profile...')
        city_setif = City.objects.get(name='Sétif')
        
        company, created = Company.objects.get_or_create(
            name="EcoWaste Solutions SARL",
            defaults={
                'business_description': "Collecte et traitement des déchets industriels",
                'address_line1': "Zone Industrielle, Lot 45",
                'address_line2': "Route Nationale 5",
                'city': "setif",
                'postal_code': "16000",
                'state': city_setif,
                'phone': "+213555987654",
                'fax': "+213555987655",
                'email': "contact@ecowaste.example.com",
                'website': "https://ecowaste.example.com",
                'capital_social': Decimal("1000000.00"),
                'rc': "RC-16-B-0123456",
                'art': "ART789456123",
                'nis': "NIS123456789012",
                'nif': "NIF123456789012345",
                'rib': "RIB00021 1234567890 12",
                'tva_rate': Decimal("19.00"),
                'timbre_fiscal': Decimal("100.00"),
                'invoice_prefix': "FACT",
                'next_invoice_number': 1
            }
        )
        
        if created:
            self.stdout.write(f'  Created company: {company.name}')
        else:
            self.stdout.write(f'  Company already exists: {company.name}')
        return company

    def create_categories(self):
        self.stdout.write('Creating product categories...')
        
        categories_data = [
            {
                'name': 'Déchets Industriels',
                'description': 'Tous types de déchets industriels collectés et traités',
            },
            {
                'name': 'Déchets Chimiques',
                'description': 'Déchets chimiques nécessitant un traitement spécial',
            },
            {
                'name': 'Déchets Métalliques',
                'description': 'Métaux et alliages recyclables',
            },
            {
                'name': 'Services',
                'description': 'Services de collecte, transport et traitement',
            },
            {
                'name': 'Équipements',
                'description': 'Équipements de protection et conteneurs',
            },
        ]
        
        created_categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            created_categories.append(category)
            if created:
                self.stdout.write(f'  Created category: {category.name}')
            else:
                self.stdout.write(f'  Category already exists: {category.name}')
        
        return created_categories

    def create_products(self, categories):
        self.stdout.write('Creating products and services...')
        
        products_data = [
            # Déchets Industriels
            {
                'category': categories[0],
                'code': 'DI-001',
                'name': 'Huiles usagées',
                'description': 'Huiles industrielles usagées nécessitant un traitement spécifique',
                'unit_price': Decimal('1200.00'),
                'unit': 'TONNE',
                'is_service': False,
                'stock_quantity': Decimal('0.00'),
                'minimum_stock': Decimal('0.00'),
                'hazard_level': 'medium',
                'storage_requirements': 'Stocker dans des fûts étanches à l\'abri de la chaleur',
                'handling_instructions': 'Porter des gants et lunettes de protection',
            },
            {
                'category': categories[0],
                'code': 'DI-002',
                'name': 'Déchets de production',
                'description': 'Déchets généraux issus de la production industrielle',
                'unit_price': Decimal('800.00'),
                'unit': 'TONNE',
                'is_service': False,
                'stock_quantity': Decimal('0.00'),
                'minimum_stock': Decimal('0.00'),
                'hazard_level': 'low',
                'storage_requirements': 'Stocker dans des conteneurs adaptés',
                'handling_instructions': 'Manipulation standard avec équipement de protection',
            },
            
            # Déchets Chimiques
            {
                'category': categories[1],
                'code': 'DC-001',
                'name': 'Solvants usagés',
                'description': 'Solvants chimiques usagés à traiter spécifiquement',
                'unit_price': Decimal('1500.00'),
                'unit': 'TONNE',
                'is_service': False,
                'stock_quantity': Decimal('0.00'),
                'minimum_stock': Decimal('0.00'),
                'hazard_level': 'high',
                'storage_requirements': 'Zone ventilée, conteneurs anti-fuite, loin de toute source d\'ignition',
                'handling_instructions': 'Équipement complet de protection, masque respiratoire obligatoire',
            },
            {
                'category': categories[1],
                'code': 'DC-002',
                'name': 'Acides usagés',
                'description': 'Acides industriels usagés',
                'unit_price': Decimal('1800.00'),
                'unit': 'TONNE',
                'is_service': False,
                'stock_quantity': Decimal('0.00'),
                'minimum_stock': Decimal('0.00'),
                'hazard_level': 'critical',
                'storage_requirements': 'Conteneurs spéciaux résistants aux acides, zone sécurisée',
                'handling_instructions': 'Équipement complet anti-acide, neutralisant à proximité',
            },
            
            # Déchets Métalliques
            {
                'category': categories[2],
                'code': 'DM-001',
                'name': 'Ferraille',
                'description': 'Ferraille et acier recyclable',
                'unit_price': Decimal('600.00'),
                'unit': 'TONNE',
                'is_service': False,
                'stock_quantity': Decimal('5.00'),
                'minimum_stock': Decimal('1.00'),
                'hazard_level': 'none',
                'storage_requirements': 'Zone couverte pour éviter la corrosion',
                'handling_instructions': 'Gants de protection contre les bords coupants',
            },
            {
                'category': categories[2],
                'code': 'DM-002',
                'name': 'Aluminium',
                'description': 'Déchets d\'aluminium recyclable',
                'unit_price': Decimal('900.00'),
                'unit': 'TONNE',
                'is_service': False,
                'stock_quantity': Decimal('3.00'),
                'minimum_stock': Decimal('0.50'),
                'hazard_level': 'none',
                'storage_requirements': 'Zone sèche',
                'handling_instructions': 'Équipement standard',
            },
            
            # Services
            {
                'category': categories[3],
                'code': 'SRV-001',
                'name': 'Collecte de déchets',
                'description': 'Service de collecte de déchets industriels sur site',
                'unit_price': Decimal('5000.00'),
                'unit': 'SERVICE',
                'is_service': True,
                'stock_quantity': Decimal('0.00'),
                'minimum_stock': Decimal('0.00'),
                'hazard_level': 'none',
                'storage_requirements': '',
                'handling_instructions': '',
            },
            {
                'category': categories[3],
                'code': 'SRV-002',
                'name': 'Transport de déchets dangereux',
                'description': 'Transport sécurisé de déchets dangereux',
                'unit_price': Decimal('8000.00'),
                'unit': 'SERVICE',
                'is_service': True,
                'stock_quantity': Decimal('0.00'),
                'minimum_stock': Decimal('0.00'),
                'hazard_level': 'none',
                'storage_requirements': '',
                'handling_instructions': '',
            },
            
            # Équipements
            {
                'category': categories[4],
                'code': 'EQ-001',
                'name': 'Conteneur 1000L',
                'description': 'Conteneur industriel de 1000 litres pour déchets',
                'unit_price': Decimal('15000.00'),
                'unit': 'PIECE',
                'is_service': False,
                'stock_quantity': Decimal('10.00'),
                'minimum_stock': Decimal('2.00'),
                'hazard_level': 'none',
                'storage_requirements': 'Empilable, à l\'abri',
                'handling_instructions': 'Utiliser un chariot élévateur',
            },
            {
                'category': categories[4],
                'code': 'EQ-002',
                'name': 'Kit de protection chimique',
                'description': 'Équipement complet de protection pour manipulation de produits chimiques',
                'unit_price': Decimal('2500.00'),
                'unit': 'PIECE',
                'is_service': False,
                'stock_quantity': Decimal('15.00'),
                'minimum_stock': Decimal('5.00'),
                'hazard_level': 'none',
                'storage_requirements': 'Zone sèche et propre',
                'handling_instructions': 'Vérifier l\'intégrité avant utilisation',
            },
        ]
        
        created_products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                code=prod_data['code'],
                defaults=prod_data
            )
            created_products.append(product)
            if created:
                self.stdout.write(f'  Created product: {product.code} - {product.name}')
            else:
                self.stdout.write(f'  Product already exists: {product.code}')
        
        return created_products

    def create_customers(self):
        self.stdout.write('Creating customers...')
        
        # First, get the City objects that we need
        city_alger = City.objects.get(name='Alger')
        city_bejaia = City.objects.get(name='Béjaïa')
        city_constantine = City.objects.get(name='Constantine')
        city_blida = City.objects.get(name='Blida')
        city_oran = City.objects.get(name='Oran')
        
        customers_data = [
            {
                'name': 'Sonatrach',
                'customer_type': 'company',
                'address_line1': 'Avenue 1 Novembre',
                'city': "alger",
                'postal_code': '16000',
                'state': city_alger,
                'phone': '+213555111222',
                'fax': '+213555111223',
                'email': 'contact@sonatrach.example.com',
                'activity': 'Pétrole et Gaz',
                'nis': 'NIS987654321098',
                'rc': 'RC-16-B-9876543',
                'art': 'ART123456789',
                'nif': 'NIF987654321098765',
                'credit_limit': Decimal('500000.00'),
                'payment_terms': 45,
                'discount_rate': Decimal('5.00'),
            },
            {
                'name': 'SNVI',
                'customer_type': 'company',
                'address_line1': 'Zone Industrielle Rouiba',
                'city': "alger",
                'postal_code': '16012',
                'state': city_alger,
                'phone': '+213555333444',
                'email': 'contact@snvi.example.com',
                'activity': 'Industrie Automobile',
                'nis': 'NIS8765432109876',
                'rc': 'RC-16-B-765432',
                'nif': 'NIF876543210987654',
                'credit_limit': Decimal('300000.00'),
                'payment_terms': 30,
            },
            {
                'name': 'Cevital',
                'customer_type': 'company',
                'address_line1': 'Route de Cap Djinet',
                'city': "bejaia",
                'postal_code': '06000',
                'state': city_bejaia,
                'phone': '+213555555666',
                'email': 'contact@cevital.example.com',
                'activity': 'Agroalimentaire',
                'nis': 'NIS7654321098765',
                'rc': 'RC-06-B-654321',
                'nif': 'NIF765432109876543',
                'credit_limit': Decimal('400000.00'),
                'payment_terms': 60,
                'discount_rate': Decimal('3.00'),
            },
            {
                'name': 'Ahmed Benali',
                'customer_type': 'individual',
                'address_line1': 'Cité El Amel, Bloc 5',
                'city': "constantine",
                'postal_code': '25000',
                'state': city_constantine,
                'phone': '+213555777888',
                'email': 'ahmed.benali@example.com',
                'payment_terms': 15,
            },
        ]
        
        created_customers = []
        for cust_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                name=cust_data['name'],
                defaults=cust_data
            )
            created_customers.append(customer)
            if created:
                self.stdout.write(f'  Created customer: {customer.name}')
            else:
                self.stdout.write(f'  Customer already exists: {customer.name}')
        
        return created_customers
    
    def create_suppliers(self):
        self.stdout.write('Creating suppliers...')
        
        # Get City objects
        city_blida = City.objects.get(name='Blida')
        city_alger = City.objects.get(name='Alger')
        city_oran = City.objects.get(name='Oran')
        
        suppliers_data = [
            {
                'name': 'TransportAlg SARL',
                'contact_person': 'Mohamed Hadj',
                'address_line1': 'Route de Blida, Zone d\'activité',
                'city': "blida",
                'postal_code': '09000',
                'state': city_blida,
                'phone': '+213555999000',
                'email': 'contact@transportalg.example.com',
                'services_provided': 'Transport de déchets industriels',
                'rc': 'RC-09-B-123789',
                'nis': 'NIS654321098765',
                'nif': 'NIF654321098765432',
                'payment_terms': 30,
                'rating': 4,
            },
            {
                'name': 'SafetyEquip EURL',
                'contact_person': 'Karim Bentahar',
                'address_line1': '15 Rue des Frères Bouadou',
                'city': "alger",
                'postal_code': '16003',
                'state': city_alger,
                'phone': '+213555888999',
                'email': 'contact@safetyequip.example.com',
                'services_provided': 'Fourniture d\'équipements de sécurité',
                'rc': 'RC-16-B-987123',
                'nis': 'NIS543210987654',
                'nif': 'NIF543210987654321',
                'payment_terms': 45,
                'rating': 5,
            },
            {
                'name': 'ChemContainer SPA',
                'contact_person': 'Amina Larbi',
                'address_line1': 'Zone Industrielle, Lot 32',
                'city': "oran",
                'postal_code': '31000',
                'state': city_oran,
                'phone': '+213555777666',
                'email': 'contact@chemcontainer.example.com',
                'services_provided': 'Fabrication de conteneurs spécialisés pour produits chimiques',
                'rc': 'RC-31-B-456789',
                'nis': 'NIS432109876543',
                'nif': 'NIF432109876543210',
                'payment_terms': 60,
                'rating': 3,
            },
        ]
        
        created_suppliers = []
        for supp_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=supp_data['name'],
                defaults=supp_data
            )
            created_suppliers.append(supplier)
            if created:
                self.stdout.write(f'  Created supplier: {supplier.name}')
            else:
                self.stdout.write(f'  Supplier already exists: {supplier.name}')
        
        return created_suppliers

    def create_stock_movements(self, products, users):
        self.stdout.write('Creating stock movements...')
        
        # Get an operator user for the stock movements
        operator_user = next((u for u in users if u.role == 'operator'), users[0])
        
        # Only create movements for physical products (not services)
        physical_products = [p for p in products if not p.is_service]
        
        # Create some initial stock entries
        for product in physical_products:
            # Skip if movements already exist for this product
            if StockMovement.objects.filter(product=product).exists():
                continue
                
            # Initial stock entry
            initial_quantity = Decimal(str(random.uniform(5.0, 20.0)))
            movement = StockMovement.objects.create(
                product=product,
                movement_type='in',
                quantity=initial_quantity,
                reference='Stock initial',
                notes='Enregistrement du stock initial',
                created_by=operator_user,
            )
            
            # Update product stock
            product.stock_quantity = initial_quantity
            product.save()
            
            self.stdout.write(f'  Created initial stock for: {product.name} - Quantity: {initial_quantity}')
            
            # Add some random movements
            for _ in range(random.randint(1, 3)):
                movement_type = random.choice(['in', 'out'])
                quantity = Decimal(str(random.uniform(1.0, 5.0)))
                
                # Skip if trying to remove more stock than available
                if movement_type == 'out' and product.stock_quantity < quantity:
                    continue
                
                movement = StockMovement.objects.create(
                    product=product,
                    movement_type=movement_type,
                    quantity=quantity,
                    reference=f'MVT-{random.randint(100, 999)}',
                    notes=f'{"Entrée" if movement_type == "in" else "Sortie"} de stock',
                    created_by=operator_user,
                )
                
                # Update product stock
                if movement_type == 'in':
                    product.stock_quantity += quantity
                else:
                    product.stock_quantity -= quantity
                product.save()
                
                self.stdout.write(f'  Created movement: {movement_type} {quantity} for {product.name}')

    def create_invoices_and_payments(self, company, customers, products, users):
        self.stdout.write('Creating invoices and payments...')
        
        # Get an accountant user for the invoices
        created_by = next((u for u in users if u.role == 'accountant'), users[0])
        
        today = date.today()
        
        # Create a few invoices for each customer
        for customer in customers:
            # Skip if invoices already exist for this customer
            if Invoice.objects.filter(customer=customer).exists():
                continue
                
            for i in range(random.randint(1, 3)):
                # Generate random dates within the last 90 days
                invoice_date = today - timedelta(days=random.randint(1, 90))
                due_date = invoice_date + timedelta(days=customer.payment_terms)
                
                # Determine status based on dates and random factors
                if invoice_date > today - timedelta(days=7):
                    status = 'draft'
                elif due_date < today and random.random() < 0.3:
                    status = 'overdue'
                elif random.random() < 0.7:
                    status = 'paid'
                else:
                    status = 'sent'
                
                # Create the invoice
                invoice = Invoice.objects.create(
                    invoice_date=invoice_date,
                    due_date=due_date,
                    customer=customer,
                    payment_method=random.choice(['cash', 'check', 'transfer', 'card']),
                    driver_name=random.choice(['', 'Karim Benzema', 'Ali Hassan', 'Omar Fadel']),
                    vehicle_registration=random.choice(['', '12345-16-01', '54321-16-02']),
                    destination=customer.city,
                    status=status,
                    notes=random.choice([
                        '',
                        'Livraison effectuée le même jour',
                        'Client satisfait du service',
                        'Demande spéciale traitée',
                    ]),
                    timbre_fiscal=company.timbre_fiscal,
                    created_by=created_by,
                )
                
                # Add 1-5 random line items
                num_items = random.randint(1, 5)
                selected_products = random.sample(list(products), min(num_items, len(products)))
                
                for product in selected_products:
                    quantity = Decimal(str(random.uniform(0.5, 10.0)))
                    unit_price = product.unit_price * Decimal(str(random.uniform(0.9, 1.1)))  # Slight price variation
                    
                    InvoiceLine.objects.create(
                        invoice=invoice,
                        product=product,
                        reference=product.code,
                        description=product.name,
                        unit=product.unit,
                        quantity=quantity,
                        unit_price=unit_price,
                    )
                
                # Apply customer discount if any
                if customer.discount_rate > 0:
                    invoice.discount_amount = invoice.subtotal_ht * (customer.discount_rate / 100)
                    invoice.save()
                
                # Create payment if invoice is paid
                if invoice.status == 'paid':
                    payment_date = invoice.invoice_date + timedelta(days=random.randint(1, 15))
                    
                    Payment.objects.create(
                        invoice=invoice,
                        amount=invoice.total_ttc,
                        payment_date=payment_date,
                        payment_method=invoice.payment_method,
                        reference=f'PAY-{random.randint(1000, 9999)}',
                        notes=random.choice(['', 'Paiement reçu avec remerciements', 'Confirmation par téléphone']),
                        created_by=created_by,
                    )
                
                self.stdout.write(f'  Created invoice: {invoice.invoice_number} for {customer.name} - {status}')