from django.conf.urls import url

from .views import healthcheck

from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('healthcheck/', healthcheck.as_view(), name='healthcheck'),
]
