# Django Laboratory Waste Management & Invoice System - AI Generation Prompt

## Project Overview

a comprehensive laboratory waste management and invoice system using Django framework with the following technology stack:

- **Backend**: Django 4.x with Python 3.x
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Charts**: Chart.js
- **Database**: sqlite

## System Requirements Based on Reference Invoice

### 1. Company Profile Management

Based on the invoice header "COLLECTE DES DECHETS SPECIAUX DANGEREUX":

```python
# Company model structure
- Company name
- Business type (Waste collection services)
- Address (multi-line support)
- Phone, Fax, Email
- Legal identifiers (RC, ART, NIS, NIF, RIB)
- Capital social
- Logo upload capability
- Tax settings and rates
```

### 2. Customer Management System

Based on client section "BOUGUERA ZAHRA":

```python
# Customer model structure
- Customer name/company
- Customer type (Individual/Company)
- Address (multi-line)
- Activity/Business sector
- Legal identifiers (NIS, RC, ART)
- Contact information
- Credit limit
- Payment terms
- Customer status (Active/Inactive)
```

### 3. Product/Service Inventory Management

Based on invoice line "COLLECT DECHET SPECIAUX":

```python
# Product/Service model structure
- Product/Service code
- Name and description
- Category (Waste collection types)
- Unit of measure (KG, Pieces, etc.)
- Unit price
- Stock quantity (for materials)
- Minimum stock level
- Supplier information
- Hazard classification (for dangerous waste)
- Storage requirements
```

### 4. Invoice Management System

Replicate the exact invoice format with:

#### Invoice Header

- Invoice number generation (auto-increment)
- Invoice date
- Due date
- Payment method (CHEQUE, CASH, TRANSFER)
- Customer information display

#### Invoice Body

- Line items with:
  - Reference number
  - Product/Service description
  - Unit of measure
  - Quantity
  - Unit price (HT - excluding tax)
  - Line total

#### Invoice Footer Calculations

- TOTAL H.T. (Total excluding tax)
- T.V.A. (VAT calculation)
- T.T.C. (Total including tax)
- TIMBRE (Stamp duty)
- AUTRES TAXES (Other taxes)
- REMISE (Discount)
- TOTAL FACTURE (Final total)

#### Additional Invoice Fields

- Driver information
- Vehicle registration
- Destination details
- Special notes section (as shown in French text area)

### 5. Provider/Supplier Management

```python
# Supplier model structure
- Supplier name/company
- Contact person
- Address and contact details
- Products/services supplied
- Payment terms
- Supplier rating
- Contract details
```

### 6. Authentication & User Management

```python
# User roles and permissions
- Admin (full access)
- Manager (invoice management, reports)
- Operator (basic invoice creation)
- Accountant (financial reports, tax management)
- Client (view own invoices only)
```

### 7. Dashboard & Analytics

Create comprehensive dashboard with:

#### Key Metrics Cards

- Total revenue (monthly/yearly)
- Outstanding invoices
- Top customers
- Inventory alerts
- Recent transactions

#### Charts & Visualizations

- Revenue trends (line chart)
- Invoice status distribution (pie chart)
- Top products/services (bar chart)
- Customer payment patterns
- Monthly/quarterly comparisons

### 8. Reports & Export System

Generate reports for:

- Invoice reports (PDF/Excel)
- Customer statements
- Product/service performance
- Tax reports (TVA declarations)
- Aged receivables
- Inventory reports

## Technical Implementation Details

### Django Project Structure

```miasm
project/
├── apps/
│   ├── authentication/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── create_superuser.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── company/
│   │   ├── admin.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── customers/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── populate_cities.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── dashboard/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── populate_db.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── inventory/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── invoices/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── templatetags/
│   │   │   └── custom_filters.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── reports/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   └── views.py
│   └── suppliers/
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── migrations/
│       │   └── 0001_initial.py
│       ├── models.py
│       ├── urls.py
│       └── views.py
├── config/
│   ├── settings.py
│   ├── resources.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── manage.py
├── requirements.txt
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/
    ├── authentication/
    │   ├── login.html
    │   ├── profile.html
    │   └── register.html
    ├── base.html
    ├── company/
    │   └── settings.html
    ├── customers/
    │   ├── customer_confirm_delete.html
    │   ├── customer_detail.html
    │   ├── customer_form.html
    │   └── customer_list.html
    ├── dashboard/
    │   └── index.html
    ├── inventory/
    │   ├── low_stock_report.html
    │   ├── product_detail.html
    │   ├── product_form.html
    │   ├── product_list.html
    │   └── stock_movement_form.html
    ├── invoices/
    │   ├── invoice_detail.html
    │   ├── invoice_form.html
    │   ├── invoice_list.html
    │   ├── invoice_print.html
    │   ├── payment_confirm_delete.html
    │   ├── payment_form.html
    │   ├── payment_history.html
    │   ├── payment_receipt.html
    │   └── tags/
    │       └── payment_status_badge.html
    ├── partials/
    │   ├── navbar.html
    │   └── sidebar.html
    ├── reports/
    │   ├── customer_report.html
    │   ├── financial_report.html
    │   ├── index.html
    │   ├── product_report.html
    │   └── sales_report.html
    └── suppliers/
        ├── supplier_confirm_delete.html
        ├── supplier_detail.html
        ├── supplier_form.html
        └── supplier_list.html
```

### Bootstrap 5 UI Components Required

- Navigation sidebar with collapsible menu
- Data tables with sorting/filtering
- Modal dialogs for CRUD operations
- Form validation with custom styling
- Progress bars for dashboard metrics
- Cards for statistical displays
- Responsive invoice layout
- Print-friendly invoice template

### JavaScript Functionality

- Dynamic form fields (add/remove invoice lines)
- Real-time calculations (tax, totals)
- AJAX for seamless user experience
- Form validation
- Auto-complete for customer/product selection
- Chart.js integration for analytics
- Print invoice functionality
- Export capabilities

### Database Models Priority

1. **Company**
2. **User** (extend Django's User)
3. **Customer**
4. **Supplier**
5. **Product/Service**
6. **Invoice** (with foreign keys)
7. **InvoiceLine** (invoice details)
8. **Payment** (payment tracking)

### Key Features to Implement

#### Invoice Generation

- Auto-numbering system
- Tax calculations (TVA)
- Multiple tax rates support
- Discount applications
- Payment term tracking
- Status workflow (Draft → Sent → Paid → Overdue)

#### Inventory Management

- Stock level tracking
- Low stock alerts
- Purchase order generation
- Supplier management
- Cost tracking

#### Financial Management

- Payment recording
- Outstanding balance tracking
- Credit limit monitoring
- Late payment alerts
- Financial reporting

### Security Requirements

- Role-based access control
- Data encryption for sensitive information
- Audit trail for all transactions
- Secure file uploads
- CSRF protection
- SQL injection prevention

### Localization

- French language support (primary)
- Currency formatting (Algerian Dinar)
- Date formatting (DD/MM/YYYY)
- Number formatting
- Tax terminology compliance

## Sample Code Structure Request

Please generate:

1. Complete Django models with relationships
2. Views with CRUD functionality
3. HTML templates with Bootstrap 5 styling
4. JavaScript for dynamic interactions
5. CSS for custom styling
6. URL configurations
7. Form classes with validation
8. Management commands for initial data
9. Settings configuration
10. Requirements.txt file

## Additional Features

- Email invoice sending
- SMS notifications
- Backup/restore functionality
- API endpoints for mobile app integration
- Multi-company support (future enhancement)
- Integration with accounting software
- Barcode/QR code generation for invoices

## Performance Requirements

- Fast invoice generation (<2 seconds)
- Efficient database queries
- Pagination for large datasets
- Caching for frequently accessed data
- Optimized images and assets

This system should replicate the professional appearance and functionality of the provided French invoice while adding modern web application capabilities for complete business management.

NOTICE : create me the django files and templates, for this project as per the app requirements description , no typscript, no react , no vue , only django, html, css, js
