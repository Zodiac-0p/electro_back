# user/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    # Social auth
    GoogleLoginAPIView,

    # Auth
    RegisterView,
    LoginView,
    LogoutView,
    UserDetailView,

    # Email / password
    verify_email,
    forgot_password,
    reset_password,

    # Phone (profile verify)
    send_phone_otp,
    verify_phone_otp,

    # Phone (login via OTP)
    phone_login_send_otp,
    phone_login_verify_otp,

    # Address
    AddressListCreateView,
    AddressDetailView,

    # Cart
    CartView,
    AddCartItemView,
    RemoveCartItemView,

    # Orders
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    CancelOrderView,
    DeleteOrderView,

    # Payments
    CreateRazorpayOrder,
    VerifyPaymentView,

    # Quotation / RFQ
    QuotationSubmitView,
    QuotationListView,
    QuotationDetailView,

    # Track order
    TrackOrderView,
)

urlpatterns = [
    # ---------------- AUTH ----------------
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("google-login/", GoogleLoginAPIView.as_view(), name="google-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", UserDetailView.as_view(), name="me"),

    # ---------------- EMAIL / PASSWORD ----------------
    path("verify-email/<str:uid>/<str:token>/", verify_email, name="verify-email"),
    path("auth/forgot-password/", forgot_password, name="forgot-password"),
    path("auth/reset-password/", reset_password, name="reset-password"),

    # ---------------- PHONE OTP ----------------
    # Profile phone verification (requires login if your view uses IsAuthenticated)
    path("phone/send-otp/", send_phone_otp, name="phone-send-otp"),
    path("phone/verify-otp/", verify_phone_otp, name="phone-verify-otp"),

    # Login using phone OTP (should be AllowAny)
    path("phone/login/send-otp/", phone_login_send_otp, name="phone-login-send-otp"),
    path("phone/login/verify-otp/", phone_login_verify_otp, name="phone-login-verify-otp"),

    # ---------------- ADDRESSES ----------------
    path("addresses/", AddressListCreateView.as_view(), name="addresses"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),

    # ---------------- CART ----------------
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/add/", AddCartItemView.as_view(), name="cart-add"),
    path("cart/remove/<int:pk>/", RemoveCartItemView.as_view(), name="cart-remove"),

    # ---------------- ORDERS ----------------
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:order_id>/cancel/", CancelOrderView.as_view(), name="order-cancel"),
    path("orders/<int:order_id>/delete/", DeleteOrderView.as_view(), name="order-delete"),

    # ---------------- PAYMENTS ----------------
    path("payments/create-razorpay-order/", CreateRazorpayOrder.as_view(), name="create-razorpay-order"),
    path("payments/verify/", VerifyPaymentView.as_view(), name="verify-razorpay-payment"),

    # ---------------- RFQ / QUOTATION ----------------
    path("quotation/submit/", QuotationSubmitView.as_view(), name="quotation-submit"),
    path("quotation/", QuotationListView.as_view(), name="quotation-list"),
    path("quotation/<int:pk>/", QuotationDetailView.as_view(), name="quotation-detail"),

    # ---------------- TRACK ORDER (PUBLIC) ----------------
    path("track-order/<int:order_id>/", TrackOrderView.as_view(), name="track-order"),
]