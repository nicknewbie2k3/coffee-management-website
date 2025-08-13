from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

extrapatternsadmin = [
    path('', views.admin_page, name='admin_page'),
    path('editproduct/', views.editproduct, name='edit_product'),
    path('vieworder/', views.vieworder, name='view_orders'),
]

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('makeOrder', views.make_order, name='makeOrder'), 
    path('printBill', views.print_bill, name='printBill'),
    path('adminpage/', include(extrapatternsadmin)),
    path('adminlogin/', views.admin_login, name='adminlogin'),
]