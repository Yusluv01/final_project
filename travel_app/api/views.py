from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
import json

from travel_app.models import Client, Booking, Payment, Notification

@login_required
def stats_api(request):
    """API endpoint for dashboard statistics"""
    agent = request.user
    
    stats = {
        'clients_count': Client.objects.filter(agent_assigned=agent).count(),
        'bookings_count': Booking.objects.filter(agent=agent).count(),
        'pending_documents': 0,
        'total_revenue': Payment.objects.filter(
            booking__agent=agent, 
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    return JsonResponse(stats)


class ClientsAPIView(LoginRequiredMixin, View):
    """API view for clients"""
    
    def get(self, request):
        clients = Client.objects.filter(agent_assigned=request.user).values(
            'id', 'first_name', 'last_name', 'passport_number', 
            'email', 'phone', 'travel_type'
        )
        return JsonResponse(list(clients), safe=False)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            # Create client logic here
            return JsonResponse({'success': True, 'message': 'Client created'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class BookingsAPIView(LoginRequiredMixin, View):
    """API view for bookings"""
    
    def get(self, request):
        bookings = Booking.objects.filter(agent=request.user).values(
            'id', 'booking_id', 'client__first_name', 'client__last_name',
            'status', 'total_amount', 'travel_date_start'
        )
        return JsonResponse(list(bookings), safe=False)


@login_required
def mark_notifications_read(request):
    """Mark all notifications as read"""
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid method'}, status=405)