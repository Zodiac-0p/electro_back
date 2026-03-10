from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import random
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from firebase_admin import auth as fb_auth
from rest_framework_simplejwt.tokens import RefreshToken
from config.firebase_admin import init_firebase
User = get_user_model()


import random

from .models import (
    Address,
    CartItem,
    Order,
    OrderItem,
    Payment,
    QuotationRequest,
    PhoneOTP,
)
from .razorpay_client import client
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    AddressSerializer,
    CartSerializer,
    OrderSerializer,
    QuotationRequestSerializer,
    QuotationRequestSubmitSerializer,
    OrderTrackingSerializer,
)
from .tokens import email_verification_token

User = get_user_model()


# -------------------------
# Guest Cart Helpers
# -------------------------
def get_guest_cart(request):
    return request.session.get("cart", {})


def save_guest_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


# -------------------------
# User Authentication
# -------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # ✅ lock until verified
        if hasattr(user, "is_verified"):
            user.is_verified = False
        if hasattr(user, "is_active"):
            user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)

        backend = getattr(settings, "BACKEND_URL", "http://127.0.0.1:8000")
        verify_link = f"{backend}/api/verify-email/{uid}/{token}/"

        html_message = f"""
<html>
  <body style="font-family:Arial;background:#f4f6f8;padding:20px;">
    <div style="max-width:480px;margin:auto;background:#ffffff;padding:24px;border-radius:10px;">
      <h2 style="color:#1f4fd8;text-align:center;">Welcome to ElectroBoards 🎉</h2>
      <p>Hi {user.username},</p>
      <p>Please verify your email address to activate your account.</p>
      <div style="text-align:center;margin:30px 0;">
        <a href="{verify_link}" style="background:#1f4fd8;color:white;padding:12px 20px;border-radius:6px;text-decoration:none;font-weight:bold;">
          Verify Email
        </a>
      </div>
      <p style="font-size:12px;color:#888;text-align:center;">© 2026 ElectroBoards</p>
    </div>
  </body>
</html>
"""

        email_sent = True
        try:
            send_mail(
                subject="Verify your ElectroBoards account",
                message=f"Verify your account using this link: {verify_link}",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            email_sent = False
            print("EMAIL SEND FAILED (REGISTER):", e)

        return Response(
            {
                "message": "Account created successfully. Please check your email to verify your account, then login.",
                "email_sent": email_sent,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifier = (request.data.get("identifier") or "").strip()
        password = request.data.get("password")

        if not identifier or not password:
            return Response({"detail": "Identifier and password are required"}, status=400)

        user = None

        # 1) try username directly
        user = authenticate(request, username=identifier, password=password)

        # 2) try email
        if not user:
            u = User.objects.filter(email__iexact=identifier).first()
            if u:
                user = authenticate(request, username=u.username, password=password)

        # 3) try phone number
        if not user:
            u = User.objects.filter(phone_number=identifier).first()
            if u:
                user = authenticate(request, username=u.username, password=password)

        if not user:
            return Response({"detail": "Invalid email/phone/username or password"}, status=401)

        # if you want to block unverified accounts
        if hasattr(user, "is_verified") and not user.is_verified:
            return Response({"detail": "Please verify your email first."}, status=403)

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
            }
        }, status=200)
        
        
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=200)
        except Exception:
            return Response({"error": "Invalid token"}, status=400)


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# -------------------------
# Address Management
# -------------------------
class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        address = serializer.save(user=self.request.user)

        if address.is_default:
            Address.objects.filter(
                user=self.request.user,
                address_type=address.address_type,
            ).exclude(id=address.id).update(is_default=False)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        address = serializer.save()

        if address.is_default:
            Address.objects.filter(
                user=self.request.user,
                address_type=address.address_type,
            ).exclude(id=address.id).update(is_default=False)


# -------------------------
# Cart Management (Guest + Auth)
# -------------------------
class CartView(APIView):
    permission_classes = [AllowAny]
    # allow JWTAuthentication so valid tokens populate request.user, but catch
    # AuthenticationFailed exceptions to avoid returning 401 for bad tokens.
    from rest_framework_simplejwt.authentication import JWTAuthentication
    authentication_classes = [JWTAuthentication]

    def initial(self, request, *args, **kwargs):
        from rest_framework.exceptions import AuthenticationFailed
        from django.contrib.auth.models import AnonymousUser
        try:
            super().initial(request, *args, **kwargs)
        except AuthenticationFailed:
            # treat as anonymous rather than aborting
            request.user = AnonymousUser()
            request.auth = None


    def get(self, request):
        if request.user.is_authenticated:
            cart = request.user.cart
            serializer = CartSerializer(cart)
            return Response(serializer.data)

        cart = get_guest_cart(request)
        return Response({"guest_cart": cart})


class AddCartItemView(APIView):
    permission_classes = [AllowAny]
    from rest_framework_simplejwt.authentication import JWTAuthentication
    authentication_classes = [JWTAuthentication]

    def initial(self, request, *args, **kwargs):
        from rest_framework.exceptions import AuthenticationFailed
        from django.contrib.auth.models import AnonymousUser
        try:
            super().initial(request, *args, **kwargs)
        except AuthenticationFailed:
            request.user = AnonymousUser()
            request.auth = None

    def post(self, request):
        product_id = str(request.data.get("product"))
        quantity = int(request.data.get("quantity", 1))

        if request.user.is_authenticated:
            cart = request.user.cart
            item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
            item.quantity = item.quantity + quantity if not created else quantity
            item.save()
            return Response({"message": "Item added to cart"}, status=200)

        cart = get_guest_cart(request)
        cart[product_id] = cart.get(product_id, 0) + quantity
        save_guest_cart(request, cart)
        return Response({"message": "Item added to guest cart"}, status=200)


class RemoveCartItemView(APIView):
    permission_classes = [AllowAny]
    from rest_framework_simplejwt.authentication import JWTAuthentication
    authentication_classes = [JWTAuthentication]

    def initial(self, request, *args, **kwargs):
        from rest_framework.exceptions import AuthenticationFailed
        from django.contrib.auth.models import AnonymousUser
        try:
            super().initial(request, *args, **kwargs)
        except AuthenticationFailed:
            request.user = AnonymousUser()
            request.auth = None

    def delete(self, request, pk):
        if request.user.is_authenticated:
            cart = request.user.cart
            try:
                item = CartItem.objects.get(cart=cart, id=pk)
                item.delete()
                return Response({"message": "Item removed"}, status=200)
            except CartItem.DoesNotExist:
                return Response({"error": "Item not found"}, status=404)

        cart = get_guest_cart(request)
        pk = str(pk)

        if pk in cart:
            del cart[pk]
            save_guest_cart(request, cart)
            return Response({"message": "Item removed"}, status=200)

        return Response({"error": "Item not found"}, status=404)


# -------------------------
# Orders + Payments
# -------------------------
class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = request.user.cart

        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        payment_method = request.data.get("payment_method", "cod")
        billing_address_id = request.data.get("billing_address")
        shipping_address_id = request.data.get("shipping_address")

        if not billing_address_id or not shipping_address_id:
            return Response(
                {"error": "Billing and shipping addresses are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        billing_address = Address.objects.filter(id=billing_address_id, user=request.user).first()
        shipping_address = Address.objects.filter(id=shipping_address_id, user=request.user).first()

        if not billing_address or not shipping_address:
            return Response({"error": "Invalid address"}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = sum(item.product.price * item.quantity for item in cart.items.all())

        order = Order.objects.create(
            user=request.user,
            billing_address=billing_address,
            shipping_address=shipping_address,
            total_amount=total_amount,
            status="pending",
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=total_amount,
            status="created",
        )

        response_data = {"order_id": order.id}

        if payment_method == "razorpay":
            razorpay_order = client.order.create(
                {
                    "amount": int(total_amount * 100),
                    "currency": "INR",
                    "receipt": f"order_{order.id}",
                }
            )
            payment.razorpay_order_id = razorpay_order["id"]
            payment.save(update_fields=["razorpay_order_id"])

            response_data.update(
                {
                    "razorpay_order_id": razorpay_order["id"],
                    "amount": int(total_amount * 100),
                    "key": settings.RAZORPAY_KEY_ID,
                }
            )

        if payment_method == "cod":
            cart.items.all().delete()
            order.status = "processing"
            order.save(update_fields=["status"])

        return Response(response_data, status=status.HTTP_201_CREATED)


class CreateRazorpayOrder(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = request.user.cart

        if not cart.items.exists():
            return Response({"error": "Cart empty"}, status=400)

        total_amount = sum(item.product.price * item.quantity for item in cart.items.all())

        razorpay_order = client.order.create(
            {
                "amount": int(total_amount * 100),
                "currency": "INR",
                "receipt": f"user_{request.user.id}",
            }
        )

        return Response(
            {
                "razorpay_order_id": razorpay_order["id"],
                "amount": int(total_amount * 100),
                "key": settings.RAZORPAY_KEY_ID,
            }
        )


class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data

        try:
            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": data["razorpay_order_id"],
                    "razorpay_payment_id": data["razorpay_payment_id"],
                    "razorpay_signature": data["razorpay_signature"],
                }
            )
        except Exception:
            return Response({"error": "Payment signature verification failed"}, status=400)

        cart = request.user.cart
        total_amount = sum(item.product.price * item.quantity for item in cart.items.all())

        order = Order.objects.create(
            user=request.user,
            billing_address_id=data["billing_address"],
            shipping_address_id=data["shipping_address"],
            total_amount=total_amount,
            status="processing",
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        Payment.objects.create(
            order=order,
            payment_method="razorpay",
            amount=total_amount,
            razorpay_payment_id=data["razorpay_payment_id"],
            razorpay_order_id=data["razorpay_order_id"],
            razorpay_signature=data["razorpay_signature"],
            status="paid",
        )

        cart.items.all().delete()
        return Response({"order_id": order.id})


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-id")


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.status not in ["pending", "processing"]:
            return Response(
                {"detail": "Order cannot be cancelled at this stage"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = "cancelled"
        order.save(update_fields=["status"])
        return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)


class DeleteOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.status != "cancelled":
            return Response(
                {"detail": "Only cancelled orders can be removed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.delete()
        return Response({"message": "Order removed successfully"}, status=status.HTTP_200_OK)


# -------------------------
# Track Order (PUBLIC)
# -------------------------
class TrackOrderView(APIView):
    """
    Public order tracking by Order.id
    GET /api/user/track-order/<order_id>/
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderTrackingSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------
# Email Verification
# -------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def verify_email(request, uid, token):
    try:
        uid_decoded = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid_decoded)
    except Exception:
        return Response({"error": "Invalid link"}, status=400)

    if email_verification_token.check_token(user, token):
        if hasattr(user, "is_verified"):
            user.is_verified = True

        user.is_active = True
        user.save()

        frontend_login = getattr(
            settings,
            "FRONTEND_LOGIN_URL",
            "http://127.0.0.1:3000/account/login",
        )
        return redirect(frontend_login)

    return Response({"error": "Invalid or expired token"}, status=400)


# -------------------------
# Forgot / Reset Password (OTP)
# -------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email required"}, status=400)

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"error": "No user with this email"}, status=404)

    otp = random.randint(100000, 999999)
    cache.set(f"pwd_reset_{email}", otp, timeout=300)

    html_message = f"""
    <html>
      <body style="font-family:Arial;background:#f4f6f8;padding:20px;">
        <div style="max-width:480px;margin:auto;background:#ffffff;padding:24px;border-radius:10px;">
          <h2 style="color:#ff7a00;text-align:center;">Password Reset Request 🔐</h2>
          <p>Hi {user.username},</p>
          <p>Your password reset OTP is:</p>
          <div style="font-size:26px;letter-spacing:4px;text-align:center;font-weight:bold;color:#1f4fd8;margin:20px 0;">
            {otp}
          </div>
          <p>This OTP is valid for 5 minutes.</p>
          <p style="font-size:12px;color:#888;text-align:center;">© 2026 ElectroBoards</p>
        </div>
      </body>
    </html>
    """

    try:
        send_mail(
            subject="Your ElectroBoards Password Reset OTP",
            message=f"Your OTP is: {otp}",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print("EMAIL SEND FAILED (OTP):", e)
        return Response({"error": "Unable to send email right now"}, status=500)

    return Response({"message": "OTP sent"})


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    password = request.data.get("password")

    if not email or not otp or not password:
        return Response({"error": "Missing fields"}, status=400)

    cached_otp = cache.get(f"pwd_reset_{email}")
    if not cached_otp:
        return Response({"error": "OTP expired"}, status=400)

    if str(cached_otp) != str(otp):
        return Response({"error": "Invalid OTP"}, status=400)

    user = User.objects.get(email=email)
    user.set_password(password)
    user.save()

    cache.delete(f"pwd_reset_{email}")
    return Response({"message": "Password reset successful"})


# -------------------------
# RFQ Views
# -------------------------
class QuotationSubmitView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuotationRequestSubmitSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        quotation = serializer.save(user=request.user)

        return Response(
            {
                "message": "Quotation request submitted successfully",
                "quotation": QuotationRequestSerializer(quotation).data,
            },
            status=status.HTTP_201_CREATED,
        )


class QuotationListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuotationRequestSerializer

    def get_queryset(self):
        return QuotationRequest.objects.filter(user=self.request.user)


class QuotationDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuotationRequestSerializer

    def get_queryset(self):
        return QuotationRequest.objects.filter(user=self.request.user)

User = get_user_model()
# -------------------------
# Phone OTP (Twilio)
# -------------------------
import random
from django.utils import timezone
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from .models import PhoneOTP


def normalize_india_phone(phone: str) -> str:
    phone = (phone or "").strip().replace(" ", "")
    if phone.isdigit() and len(phone) == 10:
        return "+91" + phone
    if phone.isdigit() and len(phone) == 12 and phone.startswith("91"):
        return "+" + phone
    return phone

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_phone_otp(request):
    phone = normalize_india_phone(request.data.get("phone_number"))

    if not phone.startswith("+"):
        return Response({"detail": "Phone must be like +919999999999"}, status=400)

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        verification = client.verify.v2.services(
            settings.TWILIO_VERIFY_SERVICE_SID
        ).verifications.create(
            to=phone,
            channel="sms",
            template_sid=settings.TWILIO_VERIFY_TEMPLATE_SID
        )

        print("✅ Verify send status:", verification.status)
        return Response({"detail": "OTP sent", "status": verification.status})

    except TwilioRestException as e:
        print("❌ Twilio Verify SEND error:", e.status, e.code, e.msg)
        return Response(
            {"detail": "Failed to send OTP", "twilio_message": e.msg},
            status=400
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_phone_otp(request):
    phone = normalize_india_phone(request.data.get("phone_number"))
    code = (request.data.get("otp") or "").strip()

    # ✅ Validate phone
    if not phone or not phone.startswith("+"):
        return Response({"detail": "Enter phone like +919876543210"}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Validate OTP (4-digit)
    if not code or not code.isdigit() or len(code) != 4:
        return Response({"detail": "Enter valid 4-digit OTP"}, status=status.HTTP_400_BAD_REQUEST)

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        check = client.verify.v2.services(
            settings.TWILIO_VERIFY_SERVICE_SID
        ).verification_checks.create(to=phone, code=code)

        print("✅ Verify check status:", check.status)

        if check.status == "approved":
            request.user.phone_number = phone
            request.user.save(update_fields=["phone_number"])
            return Response({"detail": "Phone verified successfully"})

        return Response({"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

    except TwilioRestException as e:
        print("❌ Twilio Verify CHECK error:", e.status, e.code, e.msg)
        return Response(
            {"detail": "OTP verification failed", "twilio_message": e.msg},
            status=status.HTTP_400_BAD_REQUEST
        )


class GoogleLoginAPIView(APIView):
    """
    Expects: { "token": "<firebase_id_token>" }
    Returns: { "access": "...", "refresh": "...", "user": {...} }
    """

    authentication_classes = []  # allow unauthenticated
    permission_classes = []      # allow anyone

    def post(self, request):
        init_firebase()

        id_token = request.data.get("token")
        if not id_token:
            return Response({"detail": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded = fb_auth.verify_id_token(id_token)
            email = decoded.get("email")
            name = decoded.get("name") or ""
            uid = decoded.get("uid")

            if not email:
                return Response({"detail": "Google account has no email"}, status=status.HTTP_400_BAD_REQUEST)

            # create/get user
            user, created = User.objects.get_or_create(email=email, defaults={
                "username": email.split("@")[0],
                "first_name": name.split(" ")[0] if name else "",
                "is_active": True,
            })

            # if username already exists conflict, ensure unique username
            if created:
                base = user.username
                i = 1
                while User.objects.filter(username=user.username).exclude(pk=user.pk).exists():
                    user.username = f"{base}{i}"
                    i += 1
                user.set_unusable_password()
                user.save()

            # generate JWT
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            return Response({
                "access": access,
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": f"Invalid token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # -------------------------
# Phone LOGIN OTP (Twilio) - PUBLIC
# -------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def phone_login_send_otp(request):
    phone = normalize_india_phone(request.data.get("phone_number"))

    if not phone or not phone.startswith("+"):
        return Response({"detail": "Phone must be like +919999999999"}, status=400)

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        verification = client.verify.v2.services(
            settings.TWILIO_VERIFY_SERVICE_SID
        ).verifications.create(to=phone, channel="sms")

        return Response({"detail": "OTP sent", "status": verification.status}, status=200)

    except TwilioRestException as e:
        return Response(
            {"detail": "We couldn’t find an account with this number. Create a new account to continue.", "twilio_message": e.msg},
            status=400
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def phone_login_verify_otp(request):
    phone = normalize_india_phone(request.data.get("phone_number"))
    code = (request.data.get("otp") or "").strip()

    if not phone or not phone.startswith("+"):
        return Response({"detail": "Phone must be like +919999999999"}, status=400)

    if not code or not code.isdigit() or len(code) != 4:
        return Response({"detail": "Enter valid 4-digit OTP"}, status=400)

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        check = client.verify.v2.services(
            settings.TWILIO_VERIFY_SERVICE_SID
        ).verification_checks.create(to=phone, code=code)

        if check.status != "approved":
            return Response({"detail": "Invalid or expired OTP"}, status=400)

        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={
                "username": f"user_{phone[-6:]}",
                "is_active": True,
            }
        )

        if created:
            base = user.username
            i = 1
            while User.objects.filter(username=user.username).exclude(pk=user.pk).exists():
                user.username = f"{base}{i}"
                i += 1
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "phone_number": user.phone_number,
                },
            },
            status=200,
        )

    except TwilioRestException as e:
        return Response(
            {"detail": "OTP verification failed", "twilio_message": e.msg},
            status=400
        )