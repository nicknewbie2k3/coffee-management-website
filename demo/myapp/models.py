from django.db import models

# Create your models (database tables) here.
class ToDoItem(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class ProductList(models.Model):
    productid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    stock = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return str(self.productid) + " - " + str(self.name) 
    
class OrderList(models.Model):
    orderid = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    order_state = models.IntegerField(choices=[(0, 'Paid'), (1, 'Unpaid')], default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    voucher_discount = models.FloatField(default=0) 
    final_price = models.FloatField(default=0)       

    def __str__(self):
        return f"Order {self.orderid} for {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(OrderList, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductList, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.orderid})"