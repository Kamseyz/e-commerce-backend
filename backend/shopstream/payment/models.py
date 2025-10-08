from django.db import models
from django.db import transaction
from product.models import Cart,Product
import uuid
from django.contrib.auth import get_user_model



User = get_user_model()

# payment model
class PaymentModel(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('abandoned', 'Abandoned'),
        ('reversed', 'Reversed'),
        ('cancelled', 'Cancelled')
    ]
    
    
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=50, unique=True, editable=False)
    paystack_reference = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"PAY_{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Payment {self.reference} by {self.user} - {self.total}"
    




# deduct the product quantity from stock after payment
class PaymentItem(models.Model):
    payment = models.ForeignKey(PaymentModel, on_delete=models.CASCADE, related_name="items")
    product= models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity= models.PositiveIntegerField()
    
        # update the product after payment
    @transaction.atomic
    def deduct_stock(self):
        if self.quantity > self.product.product_quantity:
            raise ValueError("Not enough stock")
        self.product.product_quantity -= self.quantity
        self.product.save()
        
    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"