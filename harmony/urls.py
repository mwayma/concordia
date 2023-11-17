from django.urls import path
from .views import fetch_company_status

urlpatterns = [
    # Your existing URL patterns
    path('fetch-company-status/', fetch_company_status, name='fetch_company_status'),
]