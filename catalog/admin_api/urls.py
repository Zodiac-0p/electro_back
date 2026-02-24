from rest_framework.routers import DefaultRouter
from .views import (
    AdminCategoryViewSet, AdminBrandViewSet, AdminProductViewSet,
    AdminProductImageViewSet, AdminInventoryViewSet, AdminCouponViewSet
)

router = DefaultRouter()
router.register("categories", AdminCategoryViewSet)
router.register("brands", AdminBrandViewSet)
router.register("products", AdminProductViewSet)
router.register("product-images", AdminProductImageViewSet)
router.register("inventory", AdminInventoryViewSet)
router.register("coupons", AdminCouponViewSet)

urlpatterns = router.urls
