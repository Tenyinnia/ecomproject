from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Product(models.Model):
    productName = models.CharField(max_length=250)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description=models.CharField(max_length=150)
    image = models.ImageField(upload_to='images/')
    stock = models.PositiveIntegerField()
    quantity = models.IntegerField()
    
    
    def __str__(self):
        return self.productName
    
    def save(self, *args, **kwargs):
        # On creation, set stock equal to initial_quantity
        if not self.pk:  # Check if it's a new instance
            self.stock = self.quantity
        else:
            # For existing products, keep the current stock or update it
            self.stock += kwargs.pop('add_stock', 0)  # Increment stock if specified

        super().save(*args, **kwargs)  # Call the original save method
        
    def is_in_stock(self):
        return self.stock > 0
    def get_absolute_url(self):
        return reverse('home')
    

    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.productName}"

    def get_total_price(self):
        return self.quantity * self.product.price
    
