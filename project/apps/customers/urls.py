from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # Customer management
    path('', views.customer_list, name='list'),
    path('create/', views.customer_create, name='create'),
    path('<int:pk>/', views.customer_detail, name='detail'),
    path('<int:pk>/update/', views.customer_update, name='update'),
    path('<int:pk>/delete/', views.customer_delete, name='delete'),
    
    # Subscription management
    path('subscription/<int:pk>/', views.subscription_detail, name='subscription_detail'),
    path('subscription/<int:subscription_id>/usage/', views.subscription_usage_list, name='subscription_usage_list'),
    path('subscription/<int:subscription_id>/usage/create/', views.subscription_usage_create, name='subscription_usage_create'),
    
    # AJAX endpoints
    path('api/subscription/<int:subscription_id>/', views.get_subscription_info, name='subscription_info_api'),
]