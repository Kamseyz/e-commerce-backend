from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ProductView, CartView, CartItemView, OrdersView,SearchProductView

router = DefaultRouter()
router.register(r'products', ProductView,  basename="products")
router.register(r'cart', CartView,  basename="cart")
router.register(r'cart-items', CartItemView,  basename="cart-items")
router.register(r'orders', OrdersView,  basename="orders")

urlpatterns = [
    path('', include(router.urls)),
    path('search/', SearchProductView.as_view(), name='search'),
]


