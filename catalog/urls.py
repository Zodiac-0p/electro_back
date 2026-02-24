from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, BrandViewSet, ProductViewSet,
    ProductImageViewSet, InventoryViewSet, CouponViewSet, ProductReviewListCreateView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'inventories', InventoryViewSet)
router.register(r'coupons', CouponViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("products/<int:pk>/reviews/", ProductReviewListCreateView.as_view(), name="product-reviews"),
]


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)