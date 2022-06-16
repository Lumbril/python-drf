from .main_router import urlpatterns as main
from .yasg_router import urlpatterns as yasg

from django.conf import settings
from django.contrib import admin

urlpatterns = main + yasg

admin.site.site_header = "Сore Admin"
admin.site.site_title = "Сore Admin"
admin.site.index_title = "Welcome to Сore Admin Panel"

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
