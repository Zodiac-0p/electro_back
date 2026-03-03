from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet, AdminOrderViewSet, AdminPaymentViewSet

router = DefaultRouter()
router.register("users", AdminUserViewSet)
router.register("orders", AdminOrderViewSet)
router.register("payments", AdminPaymentViewSet)
router.register(
    r"users/orders",
    AdminOrderViewSet,
    basename="admin-orders"
)

# add standalone login endpoint before router urls so /users/login/ works
from .views import AdminLoginView

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
]

urlpatterns += router.urls
