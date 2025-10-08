from .models import PaymentItem, PaymentModel
from rest_framework import serializers
from product.serializer import ProductSerializer

# payment item
class PaymentItemSerializer(serializers.ModelSerializer):
    product_detail= ProductSerializer(source="product", read_only=True)
    
    class Meta:
        model = PaymentItem
        fields=[
            'id',
            'product',
            'product_detail',
            "quantity",
            "price",
        ]
    

#payment
class PaymentSerializer(serializers.ModelSerializer):
    items = PaymentItemSerializer(many=True, read_only=True)
    
    class Meta:
        model=PaymentModel
        fields=[
            'id',
            'user',
            'total',
            'reference',
            'created_at',
            'items'
        ]