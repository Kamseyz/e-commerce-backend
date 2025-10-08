from .models import Product,Cart,CartItem,Order,OrderItem
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

#show product on frontpage
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=[
            'id',
            'product_image',
            'product_name',
            'product_price',
            'status',
            'product_quantity'
        ]
        read_only_fields = ['status']



#search for product
class SearchProductSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=100, allow_blank=False)


#carts
class CartSerializer(serializers.ModelSerializer):
    items=serializers.SerializerMethodField()
    
    class Meta:
        model=Cart
        fields = [
            'id',
            'user',
            'created_at',
            'items'
        ]
    
    def get_items(self,obj):
        items = obj.cartitem_set.all()
        return CartItemSerializer(items, many=True).data
    

#carts items
class CartItemSerializer(serializers.ModelSerializer):
    product=serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_details =ProductSerializer(source="product", read_only=True)
    
    class Meta:
        model =CartItem
        fields =[
            'id',
            'product',
            'product_details',
            'quantity',
        ]

    # validate quantity to make sure it must be more than one
    def validate_quantity(self,value):
        if value <= 0:
            raise ValidationError("Quantity must be greater than Zero")
        return value
    
    
    #validate the quantity is not more than the one avaliable in the store 
    def validate(self, attrs):
        product = attrs.get("product")
        quantity = attrs.get("quantity")
        if product and quantity and quantity > product.product_quantity:
            raise ValidationError(f"Quantity cannot be more than the avaliable ones in stock {product.product_quantity} is available,")
        return attrs
# order
class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    orders = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'date', 'orders']
