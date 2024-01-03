from django.contrib import admin
from django.urls import path, include,re_path
from core.admin_views import admin_login_view

urlpatterns = [
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
    path('admin/login/', admin_login_view, name='admin-login-view'),
    path('admin/', admin.site.urls),
    re_path(r'^', include('checker.urls')),
]
