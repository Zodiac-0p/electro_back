from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, Inventory, Coupon

# Simple registration
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Inventory)
admin.site.register(Coupon)
