from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserDetailView,

    AddressListCreateView,
    AddressDetailView,

    CartView,
    AddCartItemView,
    RemoveCartItemView,

    OrderCreateView,
    OrderListView,
    OrderDetailView,
    CancelOrderView,
    DeleteOrderView,

    CreateRazorpayOrder,
    VerifyPaymentView,

    verify_email,
    forgot_password,
    reset_password,
    verify_phone_otp,
    send_phone_otp,

    QuotationSubmitView,
    QuotationListView,
    QuotationDetailView,

    TrackOrderView,
)

urlpatterns = [
    # Auth
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("me/", UserDetailView.as_view()),
     path("phone/send-otp/", send_phone_otp),
    path("phone/verify-otp/", verify_phone_otp),

    # Email verify
    path("verify-email/<str:uid>/<str:token>/", verify_email, name="verify_email"),

    # Password reset
    path("auth/forgot-password/", forgot_password),
    path("auth/reset-password/", reset_password),

    # Addresses
    path("addresses/", AddressListCreateView.as_view()),
    path("addresses/<int:pk>/", AddressDetailView.as_view()),

    # Cart
    path("cart/", CartView.as_view()),
    path("cart/add/", AddCartItemView.as_view()),
    path("cart/remove/<int:pk>/", RemoveCartItemView.as_view()),

    # Orders
    path("orders/create/", OrderCreateView.as_view()),
    path("orders/", OrderListView.as_view()),
    path("orders/<int:pk>/", OrderDetailView.as_view()),
    path("orders/<int:order_id>/cancel/", CancelOrderView.as_view()),
    path("orders/<int:order_id>/delete/", DeleteOrderView.as_view()),

    # Payments
    path("payments/create-razorpay-order/", CreateRazorpayOrder.as_view(), name="create-razorpay-order"),
    path("payments/verify/", VerifyPaymentView.as_view(), name="verify-razorpay-payment"),

    # RFQ
    path("quotation/submit/", QuotationSubmitView.as_view(), name="quotation-submit"),
    path("quotation/", QuotationListView.as_view(), name="quotation-list"),
    path("quotation/<int:pk>/", QuotationDetailView.as_view(), name="quotation-detail"),

    # Track Order ✅
    path("track-order/<int:order_id>/", TrackOrderView.as_view(), name="track-order"),
    # path("api/user/", include("user.urls")),
]

