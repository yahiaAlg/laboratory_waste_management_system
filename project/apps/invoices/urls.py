from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    # Invoice URLs
    path('', views.invoice_list, name='list'),
    path('create/', views.invoice_create, name='create'),
    path('<int:pk>/', views.invoice_detail, name='detail'),
    path('<int:pk>/update/', views.invoice_update, name='update'),
    path('<int:pk>/print/', views.invoice_print, name='print'),
    path('<int:pk>/status/', views.invoice_status_update, name='status_update'),
    path('<int:pk>/delete/', views.invoice_delete, name='delete'),  # New delete URL
    
    # Payment URLs
    path('<int:invoice_pk>/payment/add/', views.add_payment, name='add_payment'),
    path('<int:invoice_pk>/payment/history/', views.payment_history, name='payment_history'),
    path('payment/<int:payment_pk>/receipt/', views.payment_receipt, name='payment_receipt'),
    path('payment/<int:payment_pk>/delete/', views.payment_delete, name='payment_delete'),
    
    # API URLs
    path('api/customer-subscriptions/', views.get_customer_subscriptions, name='api_customer_subscriptions'),
    path('api/customer-legal-info/', views.get_customer_legal_info, name='get_customer_legal_info'),
    path('api/product-data/', views.get_product_data, name='product_data'),
]