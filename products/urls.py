from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('edit_management/', views.edit_management, name='edit_management'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_management/', views.delete_management, name='delete_management'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
]
