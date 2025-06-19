from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('auth/', include('apps.authentication.urls')),
    path('company/', include('apps.company.urls')),
    path('customers/', include('apps.customers.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('invoices/', include('apps.invoices.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('reports/', include('apps.reports.urls')),
]
from django.contrib import admin

admin.site.site_header = "EcoWaste Solutions Administration"
admin.site.site_title = "EcoWaste Admin Portal"
admin.site.index_title = "Bienvenue dans le portail d'administration"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)