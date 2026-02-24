from rest_framework import serializers
from django.contrib.auth import get_user_model
from user.models import Order, OrderItem, Payment
from user.models import Address

User = get_user_model()

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class AdminOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"

class AdminPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        
class AdminAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "full_name",
            "phone_number",
            "company_name",
            "gst_number",
            "street_address",
            "city",
            "state",
            "postal_code",
            "country",
            "address_type",
        ]

class AdminOrderSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    items = AdminOrderItemSerializer(many=True, read_only=True)
    payment = AdminPaymentSerializer(read_only=True)

    # 🔥 THIS FIXES ADDRESS IDs
    billing_address = AdminAddressSerializer(read_only=True)
    shipping_address = AdminAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_email",
            "status",
            "total_amount",
            "created_at",
            "billing_address",
            "shipping_address",
            "items",
            "payment",
        ]
