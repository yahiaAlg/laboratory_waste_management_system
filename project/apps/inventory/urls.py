from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('stock-movement/create/', views.stock_movement_create, name='stock_movement_create'),
    path('stock-movement/create/<int:product_pk>/', views.stock_movement_create, name='stock_movement_create_for_product'),
    path('reports/low-stock/', views.low_stock_report, name='low_stock_report'),
]