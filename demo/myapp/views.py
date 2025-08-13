from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ProductList, OrderList, OrderItem

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user) 
            return redirect("home")   
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")

def logout(request):
    auth_logout(request)
    return redirect("home")

@login_required
def make_order(request):
    error = None
    entered_customer_name = ""
    products = ProductList.objects.all()
    product_boxes_data = []
    if request.method == "POST":
        entered_customer_name = request.POST.get("customer_name", "")
        i = 0
        while True:
            product_key = f"product_{i}"
            quantity_key = f"quantity_{i}"
            if product_key in request.POST and quantity_key in request.POST:
                product_id = request.POST.get(product_key)
                quantity = request.POST.get(quantity_key)
                product_boxes_data.append({
                    "product_id": product_id,
                    "quantity": quantity,
                })
                i += 1
            else:
                break

        if not product_boxes_data:
            error = "Please add at least one product."
            return render(
                request,
                "makeOrder.html",
                {
                    "products": products,
                    "error": error,
                    "entered_customer_name": entered_customer_name,
                    "product_boxes_data": product_boxes_data,
                }
            )

        insufficient_stock = []
        for box in product_boxes_data:
            try:
                product = ProductList.objects.get(productid=box["product_id"])
                qty = int(box["quantity"])
                if qty > product.stock:
                    insufficient_stock.append(product.name)
            except (ProductList.DoesNotExist, ValueError):
                error = "Invalid product or quantity."
                return render(
                    request,
                    "makeOrder.html",
                    {
                        "products": products,
                        "error": error,
                        "entered_customer_name": entered_customer_name,
                        "product_boxes_data": product_boxes_data,
                    }
                )

        if insufficient_stock:
            error = "We don't have enough stocks for: " + ", ".join(insufficient_stock)
            return render(
                request,
                "makeOrder.html",
                {
                    "products": products,
                    "error": error,
                    "entered_customer_name": entered_customer_name,
                    "product_boxes_data": product_boxes_data,
                }
            )

        order = OrderList.objects.create(
            customer_name=entered_customer_name,
            order_state=1
        )
        for box in product_boxes_data:
            product = ProductList.objects.get(productid=box["product_id"])
            qty = int(box["quantity"])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty
            )
            product.stock -= qty
            product.save()
        return redirect("printBill")


    if not product_boxes_data:
        product_boxes_data = [{"product_id": "", "quantity": ""}]
    return render(
        request,
        "makeOrder.html",
        {
            "products": products,
            "error": error,
            "entered_customer_name": entered_customer_name,
            "product_boxes_data": product_boxes_data,
        }
    )

@login_required
def print_bill(request):
    order = OrderList.objects.latest('orderid')
    order_items = order.items.all() 
    items_with_subtotal = [
        {
            "name": item.product.name,
            "quantity": item.quantity,
            "price": item.product.price,
            "subtotal": item.quantity * item.product.price,
        }
        for item in order_items
    ]
    total = sum(i["subtotal"] for i in items_with_subtotal)
    return render(request, "printBill.html", {
        "order": order,
        "items_with_subtotal": items_with_subtotal,
        "total": total,
    })

@login_required
def admin_page(request):
    if request.user.username == "admin":
        return render(request, "adminpage.html")
    else:
        return render(request, "home.html", {
            "error": "You must be logged in as admin to access the admin page."
        })

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username == "admin":
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect("admin_page") 
            else:
                return render(request, "adminlogin.html", {"error": "Invalid credentials"})
        else:
            return render(request, "adminlogin.html", {"error": "Only admin can log in here"})
    return render(request, "adminlogin.html")

def editproduct(request):
    edit_product = None
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add":
            name = request.POST.get("name")
            stock = request.POST.get("stock")
            price = request.POST.get("price")
            if name and stock and price:
                ProductList.objects.create(
                    name=name,
                    stock=int(stock),
                    price=float(price)
                )
        elif action == "delete":
            selected = request.POST.getlist("selected_products")
            ProductList.objects.filter(productid__in=selected).delete()
        elif action == "edit":
            selected = request.POST.getlist("selected_products")
            if selected:
                edit_product = ProductList.objects.get(productid=selected[0])
        elif action == "save_edit":
            productid = request.POST.get("edit_productid")
            name = request.POST.get("edit_name")
            stock = request.POST.get("edit_stock")
            price = request.POST.get("edit_price")
            product = ProductList.objects.get(productid=productid)
            product.name = name
            product.stock = int(stock)
            product.price = float(price)
            product.save()
    products = ProductList.objects.all()
    return render(request, "editproduct.html", {"products": products, "edit_product": edit_product})

def vieworder(request):
    edit_order = None
    error = None
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add":
            productid = request.POST.get("new_productid")
            quantity = request.POST.get("new_quantity")
            customer_name = request.POST.get("new_customer_name")
            order_state = request.POST.get("new_order_state")
            if not (productid and quantity and customer_name and order_state):
                error = "not enough information in the field"
            else:
                product = ProductList.objects.get(productid=productid)
                order = OrderList.objects.create(
                    customer_name=customer_name,
                    order_state=order_state
                )
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )
        elif action == "delete":
            selected = request.POST.getlist("selected_orders")
            OrderList.objects.filter(orderid__in=selected).delete()
        elif action == "edit":
            selected = request.POST.getlist("selected_orders")
            if selected:
                edit_order = OrderList.objects.get(orderid=selected[0])
        elif action == "save_edit":
            orderid = request.POST.get("edit_orderid")
            quantity = request.POST.get("edit_quantity")
            customer_name = request.POST.get("edit_customer_name")
            order_state = request.POST.get("edit_order_state")
            order = OrderList.objects.get(orderid=orderid)
            order.quantity = int(quantity)
            order.customer_name = customer_name
            order.order_state = int(order_state)
            order.save()
    orders = OrderList.objects.all()
    products = ProductList.objects.all()
    return render(request, "vieworder.html", {"orders": orders, "edit_order": edit_order, "products": products, "error": error})