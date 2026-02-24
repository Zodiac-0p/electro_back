from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from .models import Address, Cart, CartItem, Order, OrderItem, Payment, QuotationRequest
from catalog.serializers import ProductSerializer

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


# -------------------------
# Auth / User
# -------------------------
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn’t match."})
        return attrs

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            phone_number=validated_data.get("phone_number", ""),
        )
        user.set_password(validated_data["password"])
        user.save()

        Cart.objects.get_or_create(user=user)

        # Send verification email (basic link)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_link = f"http://127.0.0.1:3000/verify/{uid}/{token}"

        send_mail(
            subject="Verify your account",
            message=f"Click the link to verify your account:\n{verify_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "is_verified")
        read_only_fields = ("id", "is_verified")


# -------------------------
# Address
# -------------------------
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ("user",)


class AddressMiniSerializer(serializers.ModelSerializer):
    """Used inside Order / Tracking responses to show user-entered address fields."""
    class Meta:
        model = Address
        fields = [
            "full_name",
            "phone_number",
            "company_name",
            "gst_number",
            "street_address",
            "city",
            "state",
            "postal_code",
            "country",
        ]


# -------------------------
# Cart
# -------------------------
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "quantity", "product"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "created_at", "user"]


# -------------------------
# Orders / Payments
# -------------------------
class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product_id", "product_name", "quantity", "price"]


class PaymentSerializer(serializers.ModelSerializer):
    razorpay_key_id = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "razorpay_order_id",
            "amount",
            "status",
            "razorpay_key_id",
        ]

    def get_razorpay_key_id(self, obj):
        return settings.RAZORPAY_KEY_ID


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    billing_address = AddressMiniSerializer(read_only=True)
    shipping_address = AddressMiniSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "billing_address",
            "shipping_address",
            "total_amount",
            "status",
            "created_at",
            "items",
            "payment",
        ]
        read_only_fields = ["user", "created_at"]


class OrderTrackingSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="id", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    billing_address = AddressMiniSerializer(read_only=True)
    shipping_address = AddressMiniSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "order_id",
            "status",
            "total_amount",
            "created_at",
            "billing_address",
            "shipping_address",
            "payment",
            "items",
        ]


# -------------------------
# Quotation (RFQ)
# -------------------------
class QuotationRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = QuotationRequest
        fields = [
            "id",
            "username",
            "product_details",
            "quantity",
            "specifications",
            "delivery_location",
            "timeline",
            "business_name",
            "business_type",
            "budget",
            "status",
            "created_at",
        ]
        read_only_fields = ("id", "username", "status", "created_at")


class QuotationRequestSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationRequest
        fields = [
            "product_details",
            "quantity",
            "specifications",
            "delivery_location",
            "timeline",
            "business_name",
            "business_type",
            "budget",
        ]
