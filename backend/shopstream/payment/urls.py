from django.urls import path
from .views import verify_checkout,Checkout

urlpatterns = [
    path('checkout/', Checkout.as_view(), name='checkout'),
    path('verify/<str:reference>/', verify_checkout, name='verify-checkout'),
]


