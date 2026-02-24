from rest_framework import serializers
from catalog.models import (
    Category, Brand, Product, ProductImage, Inventory, Coupon
)

class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class AdminBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"

class AdminProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class AdminProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"

class AdminInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"

class AdminCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"
