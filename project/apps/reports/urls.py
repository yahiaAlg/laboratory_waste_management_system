from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('sales/', views.sales_report, name='sales'),
    path('customers/', views.customer_report, name='customers'),
    path('products/', views.product_report, name='products'),
    path('financial/', views.financial_report, name='financial'),
    path('export/<str:report_type>/', views.export_csv, name='export_csv'),
]