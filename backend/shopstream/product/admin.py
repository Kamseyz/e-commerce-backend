from django.contrib import admin
from .models import Product, Order, OrderItem, Cart, CartItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'status', 'product_price', 'product_quantity', 'date']
    list_filter = ['status']
    search_fields = ['product_name']   # <-- your model field is product_name, not name
    readonly_fields = ['date']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'date']   # <-- changed created_at -> date
    list_filter = ['status']
    readonly_fields = ['date']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']
    # order and product shouldn’t really be readonly in admin,
    # otherwise you can’t edit them. But if you want:
    # readonly_fields = ['order', 'product']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']   # <-- here it’s correct, model has created_at
    readonly_fields = ['created_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']
    # same here: only set readonly if you don’t want to edit them in admin
    # readonly_fields = ['cart', 'product']
