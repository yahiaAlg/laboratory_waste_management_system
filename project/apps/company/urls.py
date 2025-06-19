from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('settings/', views.company_settings, name='settings'),
]