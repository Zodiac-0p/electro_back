from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from user.models import Order, Payment
from django.contrib.auth import get_user_model
from .serializers import (
    AdminUserSerializer, AdminOrderSerializer, AdminPaymentSerializer,
)

User = get_user_model()

class AdminUserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

class AdminOrderViewSet(ModelViewSet):
    queryset = Order.objects.all().order_by("-id")
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminUser]


    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_value = request.data.get("status")

        valid_status = dict(Order.STATUS_CHOICES)
        if status_value not in valid_status:
            return Response({"error": "Invalid status"}, status=400)

        order.status = status_value
        order.save(update_fields=["status"])

        return Response({"message": "Status updated", "status": status_value})

class AdminPaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = AdminPaymentSerializer
    permission_classes = [IsAdminUser]
