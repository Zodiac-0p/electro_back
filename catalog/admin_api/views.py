from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from catalog.models import (
    Category, Brand, Product, ProductImage, Inventory, Coupon
)
from .serializers import (
    AdminCategorySerializer, AdminBrandSerializer, AdminProductSerializer,
    AdminProductImageSerializer, AdminInventorySerializer, AdminCouponSerializer
)

class AdminCategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = AdminCategorySerializer
    permission_classes = [IsAdminUser]

class AdminBrandViewSet(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = AdminBrandSerializer
    permission_classes = [IsAdminUser]

class AdminProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUser]

class AdminProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = AdminProductImageSerializer
    permission_classes = [IsAdminUser]

class AdminInventoryViewSet(ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = AdminInventorySerializer
    permission_classes = [IsAdminUser]

class AdminCouponViewSet(ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = AdminCouponSerializer
    permission_classes = [IsAdminUser]
