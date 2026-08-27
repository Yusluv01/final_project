from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
   from .models import (
    Agent,
    TravelPackage,
    Client,
    Booking,
    Document,
    Message,
    Payment,
    Notification,
    AuditLog,
    FlightSearchHistory,
)

class AgentAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'agent_id', 'role', 'email', 'is_online', 'is_active')
    list_filter = ('role', 'is_online', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'agent_id', 'email', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Agent Information', {
            'fields': ('agent_id', 'role', 'phone', 'profile_image', 'bio', 'is_online', 'last_activity')
        }),
    )

@admin.register(TravelPackage)
class TravelPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'package_type', 'price', 'duration_days', 'is_active', 'is_featured')
    list_filter = ('package_type', 'is_active', 'is_featured')
    search_fields = ('name', 'description')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'passport_number', 'email', 'phone', 'travel_type')
    search_fields = ('first_name', 'last_name', 'passport_number', 'email')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'client', 'package', 'status', 'total_amount', 'travel_date_start')
    list_filter = ('status', 'payment_status', 'travel_class')
    search_fields = ('booking_id', 'client__first_name', 'client__last_name')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'document_type', 'status', 'uploaded_at')
    list_filter = ('document_type', 'status')
    search_fields = ('booking__booking_id',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'message_type', 'status', 'sent_at')
    list_filter = ('message_type', 'status', 'priority')
    search_fields = ('recipient', 'recipient_name', 'content')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'booking', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('payment_method', 'status')
    search_fields = ('invoice_number', 'booking__booking_id')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'recipient__username')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_repr', 'timestamp')
    list_filter = ('action', 'model_name')
    search_fields = ('user__username', 'object_repr')

@admin.register(FlightSearchHistory)
class FlightSearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'origin', 'destination', 'departure_date', 'searched_at')
    list_filter = ('origin', 'destination')
    search_fields = ('user__username', 'origin', 'destination')

# Register Agent separately (since we used a custom class above)
admin.site.register(Agent, AgentAdmin)
