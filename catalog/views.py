from rest_framework import generics, viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Brand, Product, ProductImage, Inventory, Coupon,Review
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer, 
    ProductImageSerializer, InventorySerializer, CouponSerializer, ReviewSerializer
)

from django.conf import settings
import os
from django.http import HttpResponse
# Custom permission: only staff/admin
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

# --------- Category ---------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['name']

    def list(self, request, *args, **kwargs):
        """
        Override list to return top-level categories by default and include children.
        If `all=true` query param is provided, return all categories flat.
        """
        all_flag = request.query_params.get('all')
        if all_flag and all_flag.lower() in ['1', 'true', 'yes']:
            self.queryset = Category.objects.all().order_by('name')
        else:
            # top-level categories only
            self.queryset = Category.objects.filter(parent__isnull=True).order_by('name')
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

# --------- Brand ---------
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

# --------- Product ---------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
      # enable filtering by category and brand
    filterset_fields = ['category', 'brand', 'is_featured']
    search_fields = ['name', 'description']    # enable search
    ordering_fields = ['price', 'created_at', 'stock', 'average_rating']  # include rating ordering

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    # -------- Custom Actions --------

    # Featured products: ordered by popularity and rating
    @action(detail=False, methods=['get'])
    def featured(self, request):
        products = Product.objects.filter(is_featured=True, is_available=True).order_by('-popularity_score', '-average_rating')
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    # Latest products: last 20 created
    @action(detail=False, methods=['get'])
    def latest(self, request):
        products = Product.objects.filter(is_available=True).order_by('-created_at')[:20]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    # Top-rated products: order by average rating and review count
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        products = Product.objects.filter(is_available=True).order_by('-average_rating', '-review_count')[:20]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    # ✅ Latest updated products (limit to N)
    @action(detail=False, methods=['get'])
    def latest_updated(self, request):
        """
        Returns the latest updated products (e.g., 10 most recently updated)
        """
        limit = int(request.query_params.get('limit', 10))  # optional ?limit=5
        products = Product.objects.filter(is_available=True).order_by('-updated_at')[:limit]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

# --------- Product Image ---------
class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]

# --------- Inventory ---------
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAdminUser]

# --------- Coupon ---------
class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]


def debug_media(request):
    path = os.path.join(settings.MEDIA_ROOT, "product_images")
    try:
        files = os.listdir(path)
    except Exception as e:
        files = str(e)

    return HttpResponse(
        f"MEDIA_ROOT={settings.MEDIA_ROOT}<br>"
        f"FILES={files}"
    )
        
# --------- Product Reviews ---------

class ProductReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs["pk"]
        return Review.objects.filter(product_id=product_id).select_related("user")

    def perform_create(self, serializer):
        product_id = self.kwargs["pk"]
        serializer.save(user=self.request.user, product_id=product_id)

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]