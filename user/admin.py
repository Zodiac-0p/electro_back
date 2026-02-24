from django.contrib import admin
from .models import (
    User, Address, Cart, CartItem, Order, OrderItem, Payment, QuotationRequest
)

# Register custom User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "phone_number", "is_verified", "is_staff")
    search_fields = ("username", "email", "phone_number")


# Register other models
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)

@admin.register(QuotationRequest)
class QuotationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "business_name", "quantity", "status", "created_at")
    list_filter = ("status", "business_type", "timeline")
    search_fields = ("business_name", "user__username", "product_details")
