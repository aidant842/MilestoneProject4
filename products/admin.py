from django.contrib import admin
from .models import Product, Category, Material, Size, Colour

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Material)
admin.site.register(Size)
admin.site.register(Colour)
