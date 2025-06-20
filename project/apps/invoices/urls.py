from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.invoice_list, name='list'),
    path('create/', views.invoice_create, name='create'),
    path('<int:pk>/', views.invoice_detail, name='detail'),
    path('<int:pk>/update/', views.invoice_update, name='update'),
    path('<int:pk>/print/', views.invoice_print, name='print'),
    path('<int:pk>/status/', views.invoice_status_update, name='status_update'),
    path('<int:invoice_pk>/payment/add/', views.add_payment, name='add_payment'),
    path('api/product-data/', views.get_product_data, name='product_data'),
]