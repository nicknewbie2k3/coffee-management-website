from django.contrib import admin
from .models import ToDoItem, ProductList, OrderList, OrderItem

# Register your database models here to make them accessible in the admin interface.

admin.site.register(ToDoItem)
admin.site.register(ProductList)
admin.site.register(OrderList)
admin.site.register(OrderItem)