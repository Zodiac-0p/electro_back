from rest_framework import serializers
from .models import (
    Category, Brand, Product, ProductImage,
    Inventory, Coupon, Review
)


class CategorySerializer(serializers.ModelSerializer):
    # ✅ hierarchical display
    children = serializers.SerializerMethodField(read_only=True)

    # ✅ allow sending parent_id while creating/updating
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="parent",
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "parent_id", "children"]
        read_only_fields = ["parent", "children"]

    def get_children(self, obj):
        qs = obj.children.all()
        return [{"id": c.id, "name": c.name, "slug": c.slug} for c in qs]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"


# ✅ ONE clean review serializer (use everywhere)
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    class Meta:
        model = Review
        fields = ["id", "product", "user_name", "rating", "comment", "created_at"]
        read_only_fields = ["id", "product", "user_name", "created_at"]

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    inventory = InventorySerializer(read_only=True)

    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    # ✅ write fields
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        source="brand",
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "discount_price",
            "stock",
            "is_available",
            "is_featured",
            "category",
            "brand",
            "category_id",
            "brand_id",
            "images",
            "inventory",
            "average_rating",
            "review_count",
            "created_at",
            "updated_at",
        ]