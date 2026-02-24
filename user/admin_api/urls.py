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

urlpatterns = router.urls
