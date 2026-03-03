from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, Inventory, Coupon


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'parent')
	search_fields = ('name', 'slug')
	list_filter = ('parent',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')


admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Inventory)
admin.site.register(Coupon)
