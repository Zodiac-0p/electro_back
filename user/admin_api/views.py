from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Order, Payment
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


class AdminLoginView(APIView):
    """Authenticate admin users and return JWT tokens.

    POST /api/admin/users/login/ expects "identifier" and "password" same as
    normal login but will only succeed if the user has ``is_staff`` or
    ``is_superuser`` True.  The endpoint is mounted in ``admin_api/urls.py``.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifier = (request.data.get("identifier") or "").strip()
        password = request.data.get("password")

        if not identifier or not password:
            return Response({"detail": "Identifier and password are required"}, status=400)

        # log each attempt without exposing password
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Admin login attempt identifier={identifier}")

        # Instead of relying on authenticate() alone (which picks the first
        # matching username), perform our own lookup across username/email/phone
        # and verify the password.  This avoids a scenario where multiple users
        # share the same email/phone and the non-staff one is checked first,
        # causing a misleading "not admin" response even though an admin account
        # exists with the same identifier.
        from django.db.models import Q

        candidates = User.objects.filter(
            Q(username__iexact=identifier) |
            Q(email__iexact=identifier) |
            Q(phone_number__iexact=identifier)
        )

        user = None
        non_admin_match = False
        # Prefer staff/superuser accounts, else we risk a normal user shadowing an
        # admin when identifiers collide (e.g. someone's username equals another
        # user's phone number).
        admins_q = Q(is_staff=True) | Q(is_superuser=True)
        for u in candidates.filter(admins_q):
            if u.check_password(password):
                user = u
                break

        if not user:
            # No matching admin found, now search the remaining users.
            for u in candidates.exclude(admins_q):
                if u.check_password(password):
                    non_admin_match = True
                    break

        if not user and not non_admin_match:
            # fall back to default authentication only if we haven't already
            # located a non-admin with the correct password
            user = authenticate(request, username=identifier, password=password)

        if non_admin_match and not user:
            logger.warning(f"Admin login failed: non-admin user matched identifier={identifier}")
            # we found a non-admin with the right password, treat it as bad
            return Response({"detail": "Invalid credentials"}, status=401)

        if not user:
            logger.warning(f"Admin login failed: no matching user for identifier={identifier}")
            return Response({"detail": "Invalid credentials"}, status=401)

        # Final admin check
        if not (user.is_staff or user.is_superuser):
            return Response({"detail": "User is not an admin"}, status=403)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                # expose admin flags so frontend can verify without guessing
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        }, status=200)
