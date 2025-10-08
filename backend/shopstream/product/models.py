from django.db import models,transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model



User = get_user_model()


#product
class Product(models.Model):
    PRODUCT_CHOICES = (
        ('IN_STOCK', 'In Stock'),
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
    )
    product_name = models.CharField(max_length=100, blank=False,null=False, unique=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2) 
    product_image = models.ImageField(upload_to='product_image')
    product_quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=PRODUCT_CHOICES, default='IN_STOCK')
    date = models.DateTimeField(auto_now_add=True)
    
    
    #update status according to the product stock
    def save(self, *args, **kwargs):
        if self.product_quantity == 0:
            self.status = "OUT_OF_STOCK"
        elif self.product_quantity < 10:
            self.status = "LOW_STOCK"
        else:
            self.status = "IN_STOCK"
        return super().save(*args, **kwargs)
    
    
    #notify when the product is below 10
    def lowstock(self):
        if self.product_quantity < 10:
            raise ValidationError(f"The product {self.product_name} is almost out of stock, {self.product_quantity} in stock")
        
    #arrange the product according to date and status
    class Meta:
        ordering = ['date', 'status']
    
    def __str__(self):
        return f"The product {self.product_name} is {self.status}"
            

#cart
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.user} added {self.id}"

    def total(self):
        return sum(item.cart_total() for item in self.cartitem_set.all())
    
    

#cartitems
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    
    
    


#orders
class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order_item")
    status = models.CharField(max_length=25, choices=ORDER_STATUS_CHOICES, default='PENDING')
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Order {self.id} ({self.status})'
    
    
    
#order items
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    
    def save(self, *args, **kwargs): 
        if not self.price:
            self.price = self.product.product_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.product_name} in Order {self.order.id}"
    


