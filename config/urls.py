from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from core.admin_views import admin_login_view

urlpatterns = [
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
    path('admin/login/', admin_login_view, name='admin-login-view'),
    path('admin/', admin.site.urls),
    url(r'^', include('checker.urls')),
]
