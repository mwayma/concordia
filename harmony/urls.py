from django.urls import path
from .views import fetch_connectwise_boards

urlpatterns = [
    # Your existing URL patterns
    path('fetch-connectwise-boards/', fetch_connectwise_boards, name='fetch_connectwise_boards'),
]