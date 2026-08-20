from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
)

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.forms import PasswordResetForm

from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
    CreateView,
    UpdateView,
    DeleteView,
)

from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, FileResponse, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.decorators import method_decorator

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django import forms

from datetime import datetime, timedelta

import json
import logging
import requests
import csv
import importlib
import os
import io
import uuid
import requests

import openai

from django.core.mail import send_mail

from .models import (
    Client,
    Booking,
    TravelPackage,
    Document,
    Payment,
    Message,
    Notification,
    Agent,
    ClientDocument,
    ClientUser,
)

from .forms import (
    ClientForm,
    BookingForm,
    PaymentForm,
    MessageForm,
    ClientRegistrationForm,
    ClientDocumentUploadForm,
    AgentRegistrationForm,
)

from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
)

from .services.hotel_service import search_hotels


# Use the project's configured User model
User = get_user_model()

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):

    # Only Admin/Staff
    if not (
        request.user.is_staff
        or request.user.role in ('admin', 'staff')
    ):
        messages.warning(
            request,
            "Clients are not allowed to access the Admin Dashboard."
        )
        return redirect('travel_app:client_dashboard')

    agent = request.user

    clients_count = Client.objects.count()

    bookings_count = Booking.objects.filter(
        status__in=[
            'confirmed',
            'processing',
            'in_progress'
        ]
    ).count()

    # ================================
    # CLIENT DOCUMENTS
    # ================================

    pending_documents = (
        ClientDocument.objects
        .filter(
            is_verified=False,
            is_rejected=False
        )
        .count()
    )

    recent_documents = (
        ClientDocument.objects
        .filter(
            is_verified=False,
            is_rejected=False
        )
        .select_related('client')
        .order_by('-uploaded_at')[:10]
    )

    # ================================
    # REVENUE
    # ================================

    total_revenue = (
        Payment.objects
        .filter(status='completed')
        .aggregate(
            Sum('amount')
        )['amount__sum'] or 0
    )

    pending_invoices = (
        Booking.objects
        .filter(payment_status='pending')
        .aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
    )

    # ================================
    # CRITICAL TASKS
    # ================================

    critical_tasks = (
        Booking.objects
        .filter(
            status='pending',
            travel_date_start__gte=timezone.now().date(),
            travel_date_start__lte=(
                timezone.now().date()
                + timedelta(days=7)
            )
        )
        .select_related(
            'client',
            'package'
        )[:10]
    )

    # ================================
    # UPCOMING FLIGHTS
    # ================================

    upcoming_flights = (
        Booking.objects
        .filter(
            status='confirmed',
            travel_date_start__gte=timezone.now().date()
        )
        .select_related(
            'client',
            'package'
        )
        .order_by('travel_date_start')[:5]
    )

    context = {
        'clients_count': clients_count,
        'bookings_count': bookings_count,
        'pending_documents': pending_documents,
        'critical_tasks': critical_tasks,
        'upcoming_flights': upcoming_flights,
        'total_revenue': total_revenue,
        'pending_invoices': pending_invoices,
        'agent_name': (
            agent.get_full_name()
            or agent.username
        ),
        'agent_id': getattr(
            agent,
            'agent_id',
            'TB-0000'
        ),
        'recent_documents': recent_documents,
    }

    return render(
        request,
        'travel_app/index.html',
        context
    )


def admin_login(request):
    """
    Admin/Staff login page.

    Both Admin and Staff accounts use this login and are redirected
    to the same Admin Dashboard.
    """

    if request.user.is_authenticated:
        if (
            request.user.is_staff
            or request.user.role in ('admin', 'staff')
        ):
            return redirect('travel_app:dashboard')

        logout(request)

    login_error = None
    register_error = None

    # Default panel
    active_panel = 'login'

    # Always initialize the registration form
    form = AgentRegistrationForm()

    # ============================
    # LOGIN
    # ============================
    if request.method == 'POST' and request.POST.get('form_type') == 'login':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if (
            user is not None
            and user.is_active
            and (
                user.is_staff
                or user.role in ('admin', 'staff')
            )
        ):
            login(request, user)

            if user.first_login:
                messages.success(
                    request,
                    f'Welcome, {user.get_full_name() or user.username}!'
                )

                user.first_login = False
                user.save(update_fields=['first_login'])

            else:
                messages.success(
                    request,
                    f'Welcome back, {user.get_full_name() or user.username}!'
                )

            return redirect('travel_app:dashboard')

        else:
            login_error = (
                'Invalid admin/staff username or password. '
                'Please try again.'
            )

            # Keep Login tab active
            active_panel = 'login'

    # ============================
    # REGISTRATION
    # ============================
    elif (
        request.method == 'POST'
        and request.POST.get('form_type') == 'register'
    ):

        # Keep Registration tab active
        active_panel = 'register'

        # Bind submitted data to the form
        form = AgentRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save()

            # --------------------------------
            # SECURITY:
            # New registrations are STAFF.
            # They cannot create themselves as
            # administrators.
            # --------------------------------
            user.role = 'staff'
            user.is_staff = True
            user.is_superuser = False
            user.is_active = True

            user.save()

            messages.success(
                request,
                'Staff account created successfully! '
                'You can now log in with your username and password.'
            )

            return redirect('travel_app:admin_login')

        # Form is invalid
        register_error = (
            'Please correct the errors in the registration form.'
        )

    # ============================
    # DISPLAY PAGE
    # ============================

    return render(
        request,
        'travel_app/auth/admin_login.html',
        {
            'form': form,
            'login_error': login_error,
            'register_error': register_error,
            'active_panel': active_panel,
        }
    )

from django.contrib.auth.mixins import UserPassesTestMixin  # Add this to the top imports if not there

# ================= UPDATED ADMIN VIEWS WITH SECURITY =================
class ClientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'travel_app/clients.html'
    context_object_name = 'clients'
    paginate_by = 15
    model = Client

    def test_func(self):
        # 🔒 Only allow Staff or Admin users to access this page
        return self.request.user.is_staff

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Client.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(passport_number__icontains=query) |
                Q(email__icontains=query)
            ).order_by('-created_at')
        return Client.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_clients'] = Client.objects.count()
        context['missing_passports'] = Document.objects.filter(status='pending', document_type='passport').count()
        context['visa_approved'] = Document.objects.filter(status='verified', document_type='visa').count()
        context['student_enrolment'] = Client.objects.filter(travel_type='visa_student').count()
        return context

# Apply the exact same logic to the Detail, Create, Update, and Delete views:
class ClientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'travel_app/client_detail.html'
    context_object_name = 'client'
    model = Client

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bookings'] = Booking.objects.filter(client=self.object).select_related('package').order_by('-created_at')
        context['documents'] = Document.objects.filter(booking__client=self.object)
        return context

class ClientCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'travel_app/client_form.html'
    success_url = reverse_lazy('travel_app:clients')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Client created successfully!')
        return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'travel_app/client_form.html'
    success_url = reverse_lazy('travel_app:clients')

    def test_func(self):
        return self.request.user.is_staff
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object:
            form.fields['passport_number'].widget.attrs['disabled'] = False
            form.instance = self.object
        form.fields['new_password'] = forms.CharField(
            required=False, 
            widget=forms.PasswordInput(attrs={'placeholder': 'Leave blank to keep current password'}),
            label="New Password (Optional)"
        )
        return form
    
    def form_valid(self, form):
        new_password = form.cleaned_data.get('new_password')
        if new_password:
            self.object.set_password(new_password)
            self.object.save()
        messages.success(self.request, 'Client updated successfully!')
        return super().form_valid(form)

class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Client
    template_name = 'travel_app/client_confirm_delete.html'
    success_url = reverse_lazy('travel_app:clients')

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Client deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
class ItineraryListView(LoginRequiredMixin, ListView):
    template_name = 'travel_app/itineraries.html'
    context_object_name = 'bookings'
    paginate_by = 10
    model = Booking
    def get_queryset(self):
        return Booking.objects.all().select_related('client', 'package').order_by('-created_at')

class ItineraryDetailView(LoginRequiredMixin, DetailView):
    template_name = 'travel_app/itinerary_detail.html'
    context_object_name = 'booking'
    model = Booking
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = []
        if self.object.travel_date_start and self.object.travel_date_end:
            delta = (self.object.travel_date_end - self.object.travel_date_start).days
            days = [f"Day {i+1}" for i in range(delta + 1)]
        context['days'] = days
        return context

class ItineraryCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'travel_app/itinerary_form.html'
    success_url = reverse_lazy('travel_app:itineraries')
    def form_valid(self, form):
        form.instance.agent = self.request.user
        messages.success(self.request, 'Booking created successfully!')
        return super().form_valid(form)

@login_required
def itinerary_save(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.status = 'confirmed'
    days_text = ""
    for key, value in request.POST.items():
        if key.startswith('day_'):
            days_text += f"{key.replace('_', ' ')}: {value}\n\n"
    booking.itinerary_details = days_text
    booking.save()
    messages.success(request, f'Itinerary {booking.booking_id} has been saved!')
    return redirect('travel_app:itinerary_detail', pk=pk)

@login_required
def itinerary_share(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    client_email = booking.client.email
    subject = f"Your Itinerary for {booking.booking_id} - Travelbolt_AI"
    message = f"""
    Dear {booking.client.first_name},
    Your pilgrimage itinerary is now confirmed.
    Booking ID: {booking.booking_id}
    Travel Dates: {booking.travel_date_start} to {booking.travel_date_end}
    --- Daily Experience ---
    {booking.itinerary_details}
    """
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [client_email], fail_silently=False)
        messages.success(request, f"Itinerary sent successfully to {client_email}!")
    except Exception as e:
        messages.error(request, f"Failed to send email: {str(e)}")
    return redirect('travel_app:itinerary_detail', pk=pk)

@login_required
def itinerary_export_pdf(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    try:
        canvas = importlib.import_module('reportlab.pdfgen.canvas')
        pagesizes = importlib.import_module('reportlab.lib.pagesizes')
        letter = pagesizes.letter
    except (ImportError, ModuleNotFoundError):
        messages.error(request, 'ReportLab not installed.')
        return redirect('travel_app:itinerary_detail', pk=pk)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"Travelbolt_AI - Itinerary Report")
    p.drawString(100, 730, f"Booking ID: {booking.booking_id}")
    p.drawString(100, 710, f"Client: {booking.client.full_name}")
    p.drawString(100, 690, f"Package: {booking.package.name if booking.package else 'N/A'}")
    p.drawString(100, 670, f"Status: {booking.get_status_display()}")
    p.drawString(100, 650, f"Travel Dates: {booking.travel_date_start} to {booking.travel_date_end}")
    p.drawString(100, 630, f"Total Amount: ${booking.total_amount}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'itinerary_{booking.booking_id}.pdf')

class PaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'travel_app/payments.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_history'] = Payment.objects.all().select_related('booking').order_by('-created_at')[:20]
        confirmed_bookings = Booking.objects.filter(status='confirmed').order_by('-created_at')
        if confirmed_bookings:
            context['bookings'] = confirmed_bookings
        else:
            context['bookings'] = Booking.objects.all().order_by('-created_at')[:5]
        context['paystack_public_key'] = settings.PAYSTACK_PUBLIC_KEY
        return context

@login_required
def process_payment(request):
    if request.method == 'POST':
        messages.success(request, 'Payment processed successfully!')
        return redirect('travel_app:payment_success')
    return redirect('travel_app:payments')

class MessagingView(LoginRequiredMixin, TemplateView):
    template_name = 'travel_app/messages.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_messages'] = Message.objects.all().order_by('-sent_at')[:10]
        context['group_counts'] = {
            'hajj': Client.objects.filter(travel_type='hajj').count(),
            'umrah': Client.objects.filter(travel_type='umrah').count(),
            'student': Client.objects.filter(travel_type='visa_student').count(),
        }
        return context

@csrf_exempt
@login_required
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    try:
        message_content = request.POST.get('content', '')
        recipient_group = request.POST.get('group', 'umrah')
        attachment = request.FILES.get('attachment')
        if not message_content:
            return JsonResponse({'success': False, 'error': 'Message content is empty.'})
        file_url = None
        if attachment:
            file_name = default_storage.save(f'messages/{attachment.name}', ContentFile(attachment.read()))
            file_url = request.build_absolute_uri(settings.MEDIA_URL + file_name)
        if recipient_group == 'test':
            clients = Client.objects.filter(phone__contains='2348025460284')
        elif recipient_group == 'all':
            clients = Client.objects.all()
        else:
            clients = Client.objects.filter(travel_type=recipient_group)
        if not clients:
            return JsonResponse({'success': False, 'error': 'No clients found in this group.'})
        sent_count = 0
        failed_count = 0
        for client in clients:
            personalized_message = message_content.replace('{name}', client.full_name)
            if file_url:
                personalized_message += f"\n\n📎 Attachment: {file_url}"
            try:
                message_obj = Message.objects.create(
                    sender=request.user,
                    recipient=str(client.phone),
                    recipient_name=client.full_name,
                    message_type='whatsapp',
                    content=personalized_message,
                    status='pending'
                )
                url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
                payload = {
                    "To": f"whatsapp:{client.phone}",
                    "From": settings.TWILIO_WHATSAPP_NUMBER,
                    "Body": personalized_message
                }
                auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                response = requests.post(url, data=payload, auth=auth)
                if response.status_code == 201:
                    message_obj.status = 'sent'
                    message_obj.save()
                    sent_count += 1
                else:
                    message_obj.status = 'failed'
                    message_obj.error_message = response.text
                    message_obj.save()
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send to {client.phone}: {e}")
        return JsonResponse({
            'success': True,
            'message': f'Sent to {sent_count} clients. Failed: {failed_count}',
            'sent_count': sent_count,
            'failed_count': failed_count
        })
    except Exception as e:
        logger.error(f"Send message error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def flight_search(request):
    try:
        origin_code = request.GET.get('origin', '').upper()
        destination_code = request.GET.get('destination', '').upper()
        date = request.GET.get('date', '')
        return_date = request.GET.get('return_date', '')
        adults = int(request.GET.get('adults', 1))
        search_performed = bool(origin_code and destination_code and date)
        search_results = []
        total_results = 0
        seasonal_warning = None
        if search_performed:
            is_ogun_state_search = (origin_code == "IPERU" or origin_code == "OGUN")
            if is_ogun_state_search:
                seasonal_warning = {
                    'title': '📢 Seasonal Charter Service',
                    'message': 'Direct flights from Gateway International Airport (Iperu) to Saudi Arabia are only available during Hajj/Umrah seasons. Would you like to view flights from Lagos (LOS) instead?'
                }
                origin_code = "LOS" 
                search_performed = True
            flight_routes_db = {
                "EgyptAir": {"route": ["LOS", "CAI", "JED"], "duration": "10h 40m", "description": "Stop over at Cairo"},
                "Emirates": {"route": ["LOS", "DXB", "JED"], "duration": "9h 30m", "description": "Stop over at Dubai"},
                "Turkish Airlines": {"route": ["LOS", "IST", "JED"], "duration": "10h 15m", "description": "Stop over at Istanbul"},
                "Saudia": {"route": ["LOS", "NBO", "JED"], "duration": "14h 30m", "description": "Connection via Nairobi"},
                "Ethiopian Airlines": {"route": ["LOS", "ADD", "JED"], "duration": "8h 55m", "description": "Stop over at Addis Ababa"},
                "Qatar Airways": {"route": ["LOS", "DOH", "JED"], "duration": "9h 45m", "description": "Stop over at Doha"}
            }
            if destination_code in ["JED", "MED"]:
                import random
                airlines_list = list(flight_routes_db.keys())
                random.shuffle(airlines_list)
                selected_airlines = airlines_list[:6] 
                for i, airline_name in enumerate(selected_airlines):
                    route_data = flight_routes_db[airline_name]
                    stops_list = route_data['route']
                    duration = route_data['duration']
                    description = route_data['description']
                    route_display = " ✈ ".join(stops_list)
                    base_price = 750 if destination_code == "JED" else 850
                    price = base_price + (i * 60) - random.randint(0, 30)
                    search_results.append({
                        'id': f"FL-{origin_code}-{destination_code}-{i+1:03d}",
                        'airline': airline_name,
                        'price': round(price, 2),
                        'currency': 'USD',
                        'departure': f"{origin_code} at {random.choice(['13:40', '14:00', '10:15'])}",
                        'arrival': f"{origin_code} → {stops_list[1]} → {destination_code}",
                        'duration': duration,
                        'stops': len(stops_list) - 1,
                        'badge': "Connecting",
                        'route_display': route_display,
                        'route_description': description,
                        'protocols': 'Standard Economy',
                        'description': f'Operated by {airline_name} for Al-Iklas Hajj & Umrah Services.',
                        'booking_url': '#',
                    })
                search_results.append({
                        'id': f"FL-{origin_code}-{destination_code}-{i+2:03d}",
                        'airline': 'Saudia Direct',
                        'price': round(base_price + 150, 2),
                        'currency': 'USD',
                        'departure': f"{origin_code} at {random.choice(['12:00', '09:30'])}",
                        'arrival': f"{origin_code} → {destination_code}",
                        'duration': '5h 15m',
                        'stops': 0,
                        'badge': "Direct",
                        'route_display': f"{origin_code} ✈ {destination_code}",
                        'route_description': 'Direct flight to Saudi Arabia',
                        'protocols': 'Standard Economy',
                        'description': 'Direct flight operated by Saudia for Al-Iklas Hajj & Umrah Services.',
                        'booking_url': '#',
                    })
                total_results = len(search_results)
            else:
                search_performed = False
                total_results = 0
        context = {
            'origin_code': origin_code,
            'destination_code': destination_code,
            'date': date,
            'return_date': return_date,
            'adults': adults,
            'search_results': search_results,
            'total_results': total_results,
            'search_performed': search_performed,
            'seasonal_warning': seasonal_warning,
        }
        return render(request, 'travel_app/search.html', context)
    except Exception as e:
        logger.error(f"Flight Search Error: {e}")
        return render(request, 'travel_app/search.html', {
            'error': 'An error occurred while searching for flights.',
            'search_performed': False,
            'search_results': [],
            'total_results': 0,
        })

@login_required
def flight_search_api(request):
    origin = request.GET.get('origin', 'LHR').upper()
    destination = request.GET.get('destination', 'JED').upper()
    date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    try:
        from .services.mock_flight_service import MockFlightService
        service = MockFlightService()
        flights = service.search_flights(origin, destination, date)
        return JsonResponse({'success': True, 'flights': flights, 'count': len(flights)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e), 'flights': []})

@login_required
def explore(request):
    hotels_data = [
        {
            'name': 'Makkah Clock Royal Tower, Fairmont',
            'price': 450,
            'rating': 9.2,
            'match': 98,
            'image': 'travel_app/images/riyadh_saudi_arabia.jpg',
            'description': 'The iconic landmark overlooking the Masjid al-Haram.'
        },
        {
            'name': 'Pullman ZamZam Makkah',
            'price': 320,
            'rating': 8.9,
            'match': 95,
            'image': 'travel_app/images/Zamzam_Pullman_Makkah.jpg',
            'description': 'Modern luxury just steps from the holy mosque.'
        },
        {
            'name': 'Jabal Omar Hyatt Regency Makkah',
            'price': 450,
            'rating': 9.2,
            'match': 98,
            'image': 'travel_app/images/jabal_omar_hyatt.jpg',
            'description': 'Luxury hotel offering breathtaking views of the Kaaba.'
        }
    ]

    context = {
        'featured_destination': {
            'name': 'Makkah, Saudi Arabia',
            'description': (
                'The holiest city in Islam, home to the Masjid al-Haram '
                'and the Kaaba.'
            ),
        },
        'hotels': hotels_data,
    }

    return render(
        request,
        'travel_app/explore.html',
        context
    )

@login_required
def export_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="agency_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Client Name', 'Passport Number', 'Phone', 'Travel Type', 'Booking ID', 'Package', 'Status', 'Total Amount ($)', 'Travel Date'])
    bookings = Booking.objects.all().select_related('client', 'package').order_by('-created_at')
    for booking in bookings:
        writer.writerow([
            booking.client.full_name,
            booking.client.passport_number,
            booking.client.phone,
            booking.client.get_travel_type_display(),
            booking.booking_id,
            booking.package.name if booking.package else 'N/A',
            booking.get_status_display(),
            booking.total_amount,
            booking.travel_date_start.strftime('%Y-%m-%d'),
        ])
    return response

@csrf_exempt
@login_required(login_url='travel_app:client_login')
def ai_assistant_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('message', '').strip().lower()
            if not query:
                return JsonResponse({'success': False, 'error': 'Please enter a question.'})
            ai_response = None
            if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                try:
                    import openai
                    openai.api_key = settings.OPENAI_API_KEY
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful travel assistant specializing in Hajj, Umrah, and visa information."},
                            {"role": "user", "content": query}
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    ai_response = response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"OpenAI error: {e}")
            if ai_response:
                return JsonResponse({'success': True, 'response': ai_response})
            if 'umrah' in query or 'umra' in query:
                response = """**Umrah Visa & Document Requirements**:
1. Valid international passport with at least 6 months validity.
2. Digital photo (white background).
3. Nusuk Platform booking required.
4. Meningococcal Meningitis (ACYW135) vaccination certificate.
5. Confirmed round-trip flight tickets."""
            elif 'hajj' in query:
                response = """**Hajj Visa & Document Requirements**:
1. Hajj visa (processed via NAHCON).
2. Valid passport (6+ months).
3. Medical fitness certificate.
4. Vaccination proof (Meningitis ACYW135, Polio, Yellow Fever).
5. Biometric enrollment required."""
            elif 'visa' in query or 'document' in query:
                response = """Do you need documents for Umrah or Hajj?
- **Umrah:** Nusuk pre-booking, 6-month passport, ACYW135 vaccination.
- **Hajj:** NAHCON clearance, medical certificate, biometric enrollment.
Please tell me which one you are planning."""
            elif 'woman' in query or 'female' in query or 'mahram' in query:
                response = """**Rules for Women**:
1. Women Under 45: Must travel with a Male Guardian (Mahram). Upload Proof of Relationship.
2. Women Over 45: Permitted without a guardian, provided they upload a notarized No Objection Certificate (NOC) or travel in an organized group."""
            elif 'package' in query:
                response = """**Our Hajj & Umrah Packages:**
We offer Premium, Standard, and Economy packages ranging from $1,800 to $8,500 depending on accommodation level and distance from the Haram."""
            else:
                response = """I'm your Travelbolt AI compliance assistant. Please tell me what you are planning:
- **Umrah:** I will give you Nusuk requirements.
- **Hajj:** I will give you NAHCON rules.
- **Women traveling:** I will check if you need a Mahram."""
            return JsonResponse({'success': True, 'response': response})
        except Exception as e:
            logger.error(f"AI Assistant error: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred. Please try again.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required(login_url='travel_app:client_login')
def client_ai_assistant(request):

    # Only clients can access the AI Assistant
    if request.user.is_staff or request.user.role != 'client':
        return redirect('travel_app:dashboard')

    return render(
        request,
        'travel_app/client/ai_assistant.html'
    )

@login_required
def test_ai(request):
    test_question = "What documents do I need for Hajj?"
    response = """For Hajj, you typically need:
1. Valid passport with at least 6 months validity
2. Hajj visa (obtained through authorized agents)
3. Meningitis ACWY vaccination certificate
4. Medical fitness certificate
5. Proof of relationship for women (Mahram requirement)"""
    context = {
        'question': test_question,
        'response': response,
        'using_openai': False,
        'api_key_present': False,
    }
    return render(request, 'travel_app/test_ai.html', context)

# ==================== CLIENT PORTAL VIEWS ===================

@csrf_exempt
def magic_client_login(request, username):
    """
    TESTING ONLY:
    Log in an existing client by username.
    """
    try:
        user = User.objects.get(username=username)

        # Make sure this is actually a client account
        if user.role != 'client' or user.is_staff:
            messages.error(request, 'This account is not a valid client account.')
            return redirect('travel_app:client_login')

        login(request, user)
        messages.success(request, f'Welcome back, {user.first_name or username}!')

        return redirect('travel_app:client_dashboard')

    except User.DoesNotExist:
        messages.error(request, f'User "{username}" does not exist.')
        return redirect('travel_app:client_login')


def client_register(request):
    """
    Create a client authentication account and its Client profile.
    """

    if request.user.is_authenticated:
        if request.user.role == 'client' and not request.user.is_staff:
            return redirect('travel_app:client_dashboard')

        logout(request)

    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)

        if form.is_valid():
            from django.db import transaction

            try:
                with transaction.atomic():

                    # Save the Agent/User account.
                    # ClientRegistrationForm should create the Agent
                    # with role='client'.
                    user = form.save()

                    # Make absolutely sure this account is a client.
                    user.role = 'client'
                    user.is_staff = False
                    user.is_superuser = False
                    user.save(update_fields=[
                        'role',
                        'is_staff',
                        'is_superuser'
                    ])

                    # Create the Client profile connected to the
                    # authenticated Agent user.
                    Client.objects.create(
                        user=user,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        email=form.cleaned_data['email'],
                        phone=form.cleaned_data['phone'],
                        passport_number=form.cleaned_data.get(
                            'passport_number'
                        ) or None,
                    )

                messages.success(
                    request,
                    'Account created successfully! Please log in with your username and password.'
                )

                return redirect('travel_app:client_login')

            except Exception as exc:
                logger.exception(
                    'Client registration failed: %s',
                    exc
                )

                form.add_error(
                    None,
                    'We could not create the account. Please check your details and try again.'
                )

    else:
        form = ClientRegistrationForm()

    return render(
        request,
        'travel_app/client/register.html',
        {'form': form}
    )


def client_login(request):
    """
    Client login.

    Only users whose role is 'client' can enter
    the client portal.
    """

    # Already logged in
    if request.user.is_authenticated:

        # Client → go directly to client dashboard
        if (
            request.user.role == 'client'
            and not request.user.is_staff
        ):
            return redirect('travel_app:client_dashboard')

        # Admin/staff → log them out before showing client login
        logout(request)

    login_error = None

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            login_error = 'Please enter your username and password.'

        else:
            # Authenticate against the project's configured
            # AUTH_USER_MODEL (Agent).
            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                # IMPORTANT:
                # Only clients are allowed through this portal.
                if (
                    user.role == 'client'
                    and not user.is_staff
                    and user.is_active
                ):

                    login(request, user)

                    messages.success(
                        request,
                        f'Welcome back, {user.first_name or user.username}!'
                    )

                    # THIS IS THE IMPORTANT PART:
                    # After login, go directly to the CLIENT DASHBOARD.
                    return redirect(
                        'travel_app:client_dashboard'
                    )

                else:
                    login_error = (
                        'This login is for clients only. '
                        'Please use the appropriate portal.'
                    )

            else:
                login_error = (
                    'Invalid client username or password. '
                    'Please try again.'
                )

    return render(
        request,
        'travel_app/client/login.html',
        {
            'login_error': login_error
        }
    )


def unified_register(request):
    """
    Public registration entry point.
    """
    return client_register(request)


@login_required(login_url='travel_app:client_login')
def client_dashboard(request):
    """
    Main Client Portal Dashboard.

    After a successful client login, the client lands here.
    The dashboard only exposes information belonging to the
    currently authenticated client.
    """

    # ---------------------------------------------------------
    # ACCESS CONTROL
    # ---------------------------------------------------------

    user_role = getattr(request.user, 'role', None)

    if request.user.is_staff or user_role in ('admin', 'staff'):
        messages.warning(
            request,
            'Admins and staff must use the Admin Dashboard.'
        )
        return redirect('travel_app:dashboard')

    if user_role != 'client':
        messages.error(
            request,
            'You do not have permission to access the Client Portal.'
        )
        logout(request)
        return redirect('travel_app:client_login')

    # ---------------------------------------------------------
    # CLIENT PROFILE
    # ---------------------------------------------------------

    try:
        client = request.user.client_profile
    except Client.DoesNotExist:
        messages.error(
            request,
            'Your client profile is not linked. Please contact support.'
        )
        logout(request)
        return redirect('travel_app:client_login')

    # ---------------------------------------------------------
    # CLIENT BOOKINGS
    # ---------------------------------------------------------

    bookings = (
        Booking.objects
        .filter(client=client)
        .select_related('package')
        .order_by('-created_at')
    )

    # ---------------------------------------------------------
    # CLIENT PAYMENTS
    # ---------------------------------------------------------

    payments = (
        Payment.objects
        .filter(booking__client=client)
        .select_related('booking')
        .order_by('-created_at')
    )

    # ---------------------------------------------------------
    # CLIENT DOCUMENTS
    # ---------------------------------------------------------

    documents = (
        ClientDocument.objects
        .filter(client=client)
        .order_by('-uploaded_at')
    )

    # ---------------------------------------------------------
    # DOCUMENT COUNTS
    # ---------------------------------------------------------

    total_documents = documents.count()

    pending_documents = documents.filter(
        is_verified=False,
        is_rejected=False
    ).count()

    verified_documents = documents.filter(
        is_verified=True,
        is_rejected=False
    ).count()

    rejected_documents = documents.filter(
        is_rejected=True
    ).count()

    # ---------------------------------------------------------
    # PAYMENT TOTALS
    # ---------------------------------------------------------

    total_paid = (
        payments
        .filter(status='completed')
        .aggregate(
            Sum('amount')
        )['amount__sum']
        or 0
    )

    # ---------------------------------------------------------
    # BOOKING / TRAVEL INFORMATION
    # ---------------------------------------------------------

    active_booking = (
        bookings
        .filter(
            status__in=[
                'confirmed',
                'processing',
                'in_progress'
            ]
        )
        .first()
    )

    upcoming_booking = (
        bookings
        .filter(
            travel_date_start__gte=timezone.now().date()
        )
        .order_by('travel_date_start')
        .first()
    )

    # ---------------------------------------------------------
    # CLIENT NOTIFICATIONS
    # ---------------------------------------------------------

    notifications = (
        Notification.objects
        .filter(recipient=request.user)
        .order_by('-created_at')[:10]
    )

    # ---------------------------------------------------------
    # DASHBOARD CONTEXT
    # ---------------------------------------------------------

    context = {
        'client': client,

        # Bookings
        'bookings': bookings[:5],
        'bookings_count': bookings.count(),
        'active_booking': active_booking,
        'upcoming_booking': upcoming_booking,

        # Payments
        'payments': payments[:5],
        'payment_history': payments[:10],
        'total_paid': total_paid,
        'payments_count': payments.count(),

        # Documents
        'documents': documents[:10],
        'total_documents': total_documents,
        'pending_documents': pending_documents,
        'verified_documents': verified_documents,
        'rejected_documents': rejected_documents,

        # Notifications
        'notifications': notifications,
        'notifications_count': notifications.count(),

        # Paystack
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    }

    return render(
        request,
        'travel_app/client/dashboard.html',
        context
    )
@login_required(login_url='travel_app:client_login')
def pay_booking(request, booking_id):
    """
    Initialize a Paystack payment for a client's booking.
    """

    # Get the logged-in client's profile
    try:
        client = request.user.client_profile
    except Client.DoesNotExist:
        messages.error(
            request,
            'Your client profile is not linked. Please contact support.'
        )
        return redirect('travel_app:client_login')

    # Get ONLY this client's booking
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        client=client
    )

    # Calculate amount still owed
    balance = booking.balance_due

    # Prevent payment if already fully paid
    if balance <= 0:
        messages.info(
            request,
            'This booking has already been fully paid.'
        )
        return redirect('travel_app:client_dashboard')

    # Generate unique Paystack reference
    reference = (
        f"TB-{booking.booking_id}-"
        f"{uuid.uuid4().hex[:12].upper()}"
    )

    # Create Payment record
    payment = Payment.objects.create(
        booking=booking,
        invoice_number=(
            f"INV-{timezone.now().strftime('%Y%m')}-"
            f"{uuid.uuid4().hex[:8].upper()}"
        ),
        amount=balance,
        payment_method='paystack',
        status='pending',
        transaction_id=reference,
    )

    # Paystack expects amount in kobo
    amount_in_kobo = int(balance * 100)

    # Paystack initialization endpoint
    url = 'https://api.paystack.co/transaction/initialize'

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'email': client.email,
        'amount': amount_in_kobo,
        'currency': 'NGN',
        'reference': reference,

        'callback_url': request.build_absolute_uri(
            '/payment/paystack/callback/'
        ),

        'metadata': {
            'booking_id': booking.id,
            'booking_reference': booking.booking_id,
            'payment_id': payment.id,
            'client_id': client.id,
        }
    }

    try:

        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=30
        )

        response_data = response.json()

    except requests.RequestException as e:

        payment.status = 'failed'
        payment.notes = f'Paystack connection error: {str(e)}'

        payment.save(
            update_fields=[
                'status',
                'notes',
                'updated_at'
            ]
        )

        messages.error(
            request,
            'Unable to connect to Paystack. Please try again.'
        )

        return redirect(
            'travel_app:client_dashboard'
        )

    # Paystack initialization successful
    if response_data.get('status') is True:

        paystack_data = response_data.get('data', {})

        authorization_url = paystack_data.get(
            'authorization_url'
        )

        if authorization_url:

            payment.payment_gateway_response = response_data

            payment.save(
                update_fields=[
                    'payment_gateway_response',
                    'updated_at'
                ]
            )

            # Send client to Paystack
            return redirect(authorization_url)

    # Paystack initialization failed
    payment.status = 'failed'
    payment.payment_gateway_response = response_data
    payment.notes = response_data.get(
        'message',
        'Paystack transaction initialization failed.'
    )

    payment.save(
        update_fields=[
            'status',
            'payment_gateway_response',
            'notes',
            'updated_at'
        ]
    )

    messages.error(
        request,
        response_data.get(
            'message',
            'Payment initialization failed. Please try again.'
        )
    )

    return redirect(
        'travel_app:client_dashboard'
    )

@login_required(login_url='travel_app:client_login')
def paystack_callback(request):
    """
    Paystack redirects the client here after payment.
    The transaction is verified directly with Paystack.
    """

    reference = request.GET.get('reference')

    if not reference:
        messages.error(
            request,
            'No Paystack transaction reference was received.'
        )
        return redirect('travel_app:client_dashboard')

    # ---------------------------------------------------------
    # VERIFY TRANSACTION WITH PAYSTACK
    # ---------------------------------------------------------

    url = (
        f'https://api.paystack.co/transaction/verify/'
        f'{reference}'
    )

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response_data = response.json()

    except requests.RequestException:
        messages.error(
            request,
            'Unable to verify your payment with Paystack.'
        )
        return redirect('travel_app:client_dashboard')

    # ---------------------------------------------------------
    # CHECK PAYSTACK RESPONSE
    # ---------------------------------------------------------

    if not response_data.get('status'):
        messages.error(
            request,
            response_data.get(
                'message',
                'Payment verification failed.'
            )
        )
        return redirect('travel_app:client_dashboard')

    transaction_data = response_data.get('data', {})
    payment_status = transaction_data.get('status')

    # ---------------------------------------------------------
    # FIND PAYMENT
    # ---------------------------------------------------------

    payment = get_object_or_404(
        Payment,
        transaction_id=reference,
        booking__client=request.user.client_profile
    )

    booking = payment.booking

    # ---------------------------------------------------------
    # SUCCESSFUL PAYMENT
    # ---------------------------------------------------------

    if payment_status == 'success':

        # Prevent duplicate processing
        if payment.status == 'completed':
            return redirect(
                'travel_app:payment_success',
                payment_id=payment.id
            )

        with transaction.atomic():

            payment.status = 'completed'
            payment.paid_at = timezone.now()
            payment.transaction_id = reference
            payment.payment_gateway_response = response_data

            payment.save(
                update_fields=[
                    'status',
                    'paid_at',
                    'transaction_id',
                    'payment_gateway_response',
                    'updated_at'
                ]
            )

            # Update booking payment amount
            booking.paid_amount += payment.amount

            if booking.paid_amount >= (
                booking.total_amount -
                booking.discount_amount
            ):

                booking.paid_amount = (
                    booking.total_amount -
                    booking.discount_amount
                )

                booking.payment_status = 'paid'

            else:
                booking.payment_status = 'partial'

            booking.save(
                update_fields=[
                    'paid_amount',
                    'payment_status',
                    'updated_at'
                ]
            )

        return redirect(
            'travel_app:payment_success',
            payment_id=payment.id
        )

    # ---------------------------------------------------------
    # FAILED / DECLINED PAYMENT
    # ---------------------------------------------------------

    payment.status = 'failed'
    payment.payment_gateway_response = response_data

    payment.save(
        update_fields=[
            'status',
            'payment_gateway_response',
            'updated_at'
        ]
    )

    messages.error(
        request,
        'Payment was not successful. You have not been charged.'
    )

    return redirect('travel_app:client_dashboard')

def client_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('travel_app:client_login') 

@login_required(login_url='travel_app:client_login')
def client_flight_search(request):
    try:
        origin = request.GET.get('origin', '').upper()
        destination = request.GET.get('destination', '').upper()
        date = request.GET.get('date', '')
        return_date = request.GET.get('return_date', '')
        adults = int(request.GET.get('adults', 1))
        search_performed = bool(origin and destination and date)
        search_results = []
        total_results = 0
        if search_performed:
            from .services.letsfg_service import LetsFGService
            service = LetsFGService()
            flights = service.search_flights(origin, destination, date)
            search_results = []
            for flight in flights:
                price = 0.0
                try:
                    price = float(flight.get('price', 0))
                except:
                    price = 0.0
                stops = flight.get('stops', 0)
                if stops is None:
                    stops = 0
                search_results.append({
                    'id': flight.get('id', f"FL{len(search_results)+1:03d}"),
                    'airline': flight.get('airline', 'Unknown'),
                    'price': price,
                    'currency': flight.get('currency', 'USD'),
                    'departure': flight.get('departure', ''),
                    'arrival': flight.get('arrival', ''),
                    'duration': flight.get('duration', 'N/A'),
                    'stops': stops,
                    'badge': flight.get('badge', ''),
                    'protocols': flight.get('protocols', []),
                    'description': flight.get('description', ''),
                    'booking_url': flight.get('booking_url', ''),
                    'ai_recommended': False,
                    'ai_reason': ''
                })
            total_results = len(search_results)
        context = {
            'origin': origin,
            'destination': destination,
            'date': date,
            'return_date': return_date,
            'adults': adults,
            'search_results': search_results,
            'total_results': total_results,
            'search_performed': search_performed,
        }
        return render(request, 'client/flight_search.html', context)
    except Exception as e:
        logger.error(f"Client Flight Search error: {e}")
        return render(request, 'client/flight_search.html', {
            'error': str(e),
            'search_performed': False,
            'search_results': [],
            'total_results': 0,
        })

class ClientPasswordResetView(PasswordResetView):
    template_name = 'travel_app/client/password_reset.html'

    email_template_name = (
        'travel_app/client/password_reset_email.html'
    )

    subject_template_name = (
        'travel_app/client/password_reset_subject.txt'
    )

    success_url = reverse_lazy(
        'travel_app:client_password_reset_done'
    )


class ClientPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = (
        'travel_app/client/password_reset_confirm.html'
    )

    success_url = reverse_lazy(
        'travel_app:client_password_reset_complete'
    )


class ClientPasswordResetDoneView(PasswordResetDoneView):
    template_name = (
        'travel_app/client/password_reset_done.html'
    )


class ClientPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = (
        'travel_app/client/password_reset_complete.html'
    )


# ============================================================
# CLIENT DOCUMENT UPLOAD FORM
# ============================================================

# class ClientDocumentUploadForm(forms.ModelForm):

    class Meta:
        model = ClientDocument
        fields = ['document_type', 'file']

        widgets = {
            'document_type': forms.Select(
                attrs={
                    'class': (
                        'w-full px-3 py-2 border '
                        'border-gray-300 rounded-lg '
                        'focus:ring-2 focus:ring-blue-500'
                    )
                }
            ),

            'file': forms.FileInput(
                attrs={
                    'class': (
                        'w-full px-3 py-2 border '
                        'border-gray-300 rounded-lg '
                        'focus:ring-2 focus:ring-blue-500'
                    ),
                    'accept': (
                        '.pdf,.jpg,.jpeg,.png,.webp'
                    )
                }
            ),
        }

    def clean_file(self):

        uploaded_file = self.cleaned_data.get('file')

        if not uploaded_file:
            raise forms.ValidationError(
                'Please select a document to upload.'
            )

        # Maximum size: 10 MB
        max_size = 10 * 1024 * 1024

        if uploaded_file.size > max_size:
            raise forms.ValidationError(
                'File size must not exceed 10 MB.'
            )

        # Allowed extensions
        allowed_extensions = {
            '.pdf',
            '.jpg',
            '.jpeg',
            '.png',
            '.webp',
        }

        file_name = uploaded_file.name.lower()

        if not any(
            file_name.endswith(extension)
            for extension in allowed_extensions
        ):
            raise forms.ValidationError(
                'Invalid document format. '
                'Please upload PDF, JPG, JPEG, PNG, or WEBP files only.'
            )

        return uploaded_file


# ============================================================
# EXISTING DOCUMENT FORM
# ============================================================
# class DocumentUploadForm(forms.ModelForm):

#     class Meta:

#         model = Document

#         fields = ['document_type', 'file', 'expiry_date', 'notes']

#         widgets = {

#             'expiry_date': forms.DateInput(
#                 attrs={'type': 'date'}
#             ),

#             'notes': forms.Textarea(
#                 attrs={'rows': 2}
#             ),

#         }

@login_required(login_url='travel_app:client_login')
def client_payments(request):
    """
    Client-only payment page.
    """

    if (
        request.user.is_staff
        or request.user.role != 'client'
    ):
        messages.warning(
            request,
            'Only clients can access the client payment portal.'
        )

        return redirect('travel_app:dashboard')

    try:
        client = request.user.client_profile

    except Client.DoesNotExist:
        messages.error(
            request,
            'Your account is not linked to a Client profile.'
        )

        logout(request)

        return redirect('travel_app:client_login')

    bookings = Booking.objects.filter(
        client=client
    ).order_by('-created_at')

    payments = Payment.objects.filter(
        booking__client=client
    ).select_related(
        'booking'
    ).order_by('-created_at')

    context = {
        'client': client,
        'bookings': bookings,
        'payments': payments,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    }

    return render(
        request,
        'travel_app/client/payments.html',
        context
    )

@login_required(login_url='travel_app:client_login')
def client_payment_success(request):
    """
    Display successful client payment.
    """

    # Make sure this is a client
    if (
        request.user.is_staff
        or request.user.role != 'client'
    ):
        messages.warning(
            request,
            'Only clients can access this page.'
        )

        return redirect('travel_app:dashboard')

    ref = request.GET.get('ref')
    amount = request.GET.get('amount')

    try:
        client = request.user.client_profile
    except Client.DoesNotExist:
        messages.error(
            request,
            'Your client profile is not linked.'
        )

        logout(request)

        return redirect('travel_app:client_login')

    if ref and amount:

        booking = Booking.objects.filter(
            client=client
        ).order_by(
            '-created_at'
        ).first()

        if booking:

            Payment.objects.create(
                booking=booking,
                amount=amount,
                payment_method='card',
                status='completed',
                invoice_number=ref
            )

            messages.success(
                request,
                f'Payment of ₦{amount} completed successfully! '
                f'Reference: {ref}'
            )

        else:
            messages.warning(
                request,
                'Payment was received, but no booking was found.'
            )

    context = {
        'invoice_number': ref or 'TB-94021-X',
        'amount': f'₦{amount}' if amount else '₦12,450.00',
        'payment_date': timezone.now().strftime(
            '%B %d, %Y • %H:%M GMT'
        ),
        'payment_method': 'Paystack',
    }

    return render(
        request,
        'travel_app/client/payment_success.html',
        context
    )

@login_required
def admin_view_document(request, doc_id):
    """
    Admin document review page.

    Allows staff/admin users to inspect a client's
    uploaded document before approving or rejecting it.
    """

    # Only staff/admin users can review documents
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to review documents."
        )
        return redirect('travel_app:client_dashboard')

    document = get_object_or_404(
        ClientDocument.objects.select_related(
            'client',
            'verified_by'
        ),
        id=doc_id
    )

    return render(
        request,
        'travel_app/admin/document_review.html',
        {
            'document': document,
        }
    )

@login_required
def admin_approve_document(request, doc_id):
    """
    Approve a client's uploaded document.

    After approval:
    - Document is marked verified.
    - Client receives an in-app notification.
    - Client receives an email notification.
    """

    # Only staff/admin users can approve documents
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to approve documents."
        )
        return redirect('travel_app:client_dashboard')

    # Only POST requests are allowed
    if request.method != 'POST':
        messages.error(
            request,
            "Invalid request."
        )
        return redirect(
            'travel_app:admin_view_document',
            doc_id=doc_id
        )

    document = get_object_or_404(
        ClientDocument.objects.select_related(
            'client',
            'client__user'
        ),
        id=doc_id
    )

    # Approve the document
    document.is_verified = True
    document.is_rejected = False
    document.verified_by = request.user

    document.save(
        update_fields=[
            'is_verified',
            'is_rejected',
            'verified_by'
        ]
    )

    client = document.client
    client_user = client.user

    document_name = document.get_document_type_display()

    # ---------------------------------------------------------
    # CLIENT IN-APP NOTIFICATION
    # ---------------------------------------------------------

    if client_user:
        Notification.objects.create(
            recipient=client_user,
            title='Document Approved',
            message=(
                f'Your {document_name} has been approved '
                f'by the Travelbolt_AI travel team.'
            ),
            notification_type='success',
            link=request.build_absolute_uri(
                reverse('travel_app:client_documents')
            ),
            link_text='View Documents'
        )

    # ---------------------------------------------------------
    # CLIENT EMAIL NOTIFICATION
    # ---------------------------------------------------------

    client_email = client.email

    if client_email:

        subject = (
            f'Travelbolt_AI - {document_name} Approved'
        )

        email_message = f"""
Hello {client.first_name},

Your {document_name} has been reviewed and approved by the Travelbolt_AI travel team.

You can log in to your client portal to view your document status.

Thank you for using Travelbolt_AI.

Regards,
Travelbolt_AI
Travel Management Team
""".strip()

        try:
            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [client_email],
                fail_silently=False
            )

        except Exception as exc:
            logger.error(
                "Failed to send approval email to %s: %s",
                client_email,
                exc
            )

    # ---------------------------------------------------------
    # ADMIN MESSAGE
    # ---------------------------------------------------------

    messages.success(
        request,
        f"{document_name} for {client.full_name} "
        f"has been approved successfully."
    )

    return redirect('travel_app:dashboard')

@login_required
def admin_reject_document(request, doc_id):
    """
    Reject a client's uploaded document.

    After rejection:
    - Document is marked rejected.
    - Client receives an in-app notification.
    - Client receives an email notification.
    """

    # Only staff/admin users can reject documents
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to reject documents."
        )
        return redirect('travel_app:client_dashboard')

    # Only POST requests are allowed
    if request.method != 'POST':
        messages.error(
            request,
            "Invalid request."
        )
        return redirect(
            'travel_app:admin_view_document',
            doc_id=doc_id
        )

    document = get_object_or_404(
        ClientDocument.objects.select_related(
            'client',
            'client__user'
        ),
        id=doc_id
    )

    # Reject the document
    document.is_verified = False
    document.is_rejected = True
    document.verified_by = request.user

    document.save(
        update_fields=[
            'is_verified',
            'is_rejected',
            'verified_by'
        ]
    )

    client = document.client
    client_user = client.user

    document_name = document.get_document_type_display()

    # ---------------------------------------------------------
    # CLIENT IN-APP NOTIFICATION
    # ---------------------------------------------------------

    if client_user:
        Notification.objects.create(
            recipient=client_user,
            title='Document Rejected',
            message=(
                f'Your {document_name} was rejected after review. '
                f'Please upload a corrected document.'
            ),
            notification_type='error',
            link=request.build_absolute_uri(
                reverse('travel_app:client_upload_document')
            ),
            link_text='Upload New Document'
        )

    # ---------------------------------------------------------
    # CLIENT EMAIL NOTIFICATION
    # ---------------------------------------------------------

    client_email = client.email

    if client_email:

        subject = (
            f'Travelbolt_AI - {document_name} Requires Attention'
        )

        email_message = f"""
Hello {client.first_name},

Your {document_name} was reviewed by the Travelbolt_AI travel team and was not approved.

Please log in to your client portal and upload a corrected document.

If you need assistance, please contact the travel agency.

Thank you for using Travelbolt_AI.

Regards,
Travelbolt_AI
Travel Management Team
""".strip()

        try:
            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [client_email],
                fail_silently=False
            )

        except Exception as exc:
            logger.error(
                "Failed to send rejection email to %s: %s",
                client_email,
                exc
            )

    # ---------------------------------------------------------
    # ADMIN MESSAGE
    # ---------------------------------------------------------

    messages.warning(
        request,
        f"{document_name} for {client.full_name} "
        f"has been rejected."
    )

    return redirect('travel_app:dashboard')

@login_required
def admin_download_document(request, doc_id):
    """
    Download a client's uploaded document.
    """

    if not request.user.is_staff:
        messages.error(request, "You are not authorized to download this document.")
        return redirect('travel_app:client_dashboard')

    document = get_object_or_404(ClientDocument, id=doc_id)

    if not document.file:
        messages.error(request, "This document does not have an attached file.")
        return redirect('travel_app:dashboard')

    try:
        file_path = document.file.path

        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=document.file.name.split('/')[-1]
        )

        return response

    except FileNotFoundError:
        messages.error(request, "The document file could not be found on the server.")
        return redirect('travel_app:dashboard')

# def client_login(request):

#     # If already logged in
#     if request.user.is_authenticated:

#         user_role = getattr(request.user, 'role', None)

#         if user_role == 'client' and not request.user.is_staff:
#             return redirect('travel_app:client_dashboard')

#         logout(request)

#     login_error = None

#     if request.method == 'POST':

#         username = request.POST.get('username', '').strip()
#         password = request.POST.get('password', '')

#         user = authenticate(
#             request,
#             username=username,
#             password=password
#         )

#         user_role = getattr(user, 'role', None) if user else None

#         if (
#             user is not None
#             and user_role == 'client'
#             and not user.is_staff
#         ):
#             login(request, user)

#             messages.success(
#                 request,
#                 f'Welcome back, {user.get_full_name() or user.username}!'
#             )

#             # IMPORTANT:
#             # Client always lands on Client Portal Dashboard
#             return redirect('travel_app:client_dashboard')

#         login_error = (
#             'Invalid client username or password. Please try again.'
#         )

#     return render(
#         request,
#         'travel_app/client/login.html',
#         {
#             'login_error': login_error
#         }
#     )


@login_required(login_url='travel_app:client_login')
def client_profile(request):

    user_role = getattr(request.user, 'role', None)

    # Only clients can access this page
    if request.user.is_staff or user_role != 'client':
        return redirect('travel_app:dashboard')

    try:
        client = request.user.client_profile
    except Client.DoesNotExist:
        messages.error(
            request,
            'Your client profile is not linked. Please contact support.'
        )
        return redirect('travel_app:client_dashboard')

    return render(
        request,
        'travel_app/client/profile.html',
        {
            'client': client
        }
    )

@login_required(login_url='travel_app:client_login')
def client_documents(request):

    user_role = getattr(request.user, 'role', None)

    if request.user.is_staff or user_role != 'client':
        return redirect('travel_app:dashboard')

    try:
        client = request.user.client_profile
    except Client.DoesNotExist:
        messages.error(
            request,
            'Your client profile is not linked.'
        )
        return redirect('travel_app:client_dashboard')

    documents = (
        ClientDocument.objects
        .filter(client=client)
        .order_by('-uploaded_at')
    )

    return render(
        request,
        'travel_app/client/documents.html',
        {
            'client': client,
            'documents': documents,
        }
    )


@login_required(login_url='travel_app:client_login')
def client_upload_document(request):
    """
    Allow a logged-in client to upload their own documents.
    """

    if (
        request.user.is_staff
        or request.user.role != 'client'
    ):
        messages.warning(
            request,
            'Only clients can upload documents here.'
        )

        return redirect('travel_app:dashboard')

    try:
        client = request.user.client_profile

    except Client.DoesNotExist:
        messages.error(
            request,
            'Your account is not linked to a Client profile. '
            'Please contact support.'
        )

        logout(request)

        return redirect('travel_app:client_login')

    if request.method == 'POST':

        form = ClientDocumentUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            document = form.save(commit=False)

            document.client = client

            document.save()

            messages.success(
                request,
                'Document uploaded successfully! '
                'The admin will review it shortly.'
            )

            return redirect(
                'travel_app:client_dashboard'
            )

    else:
        form = ClientDocumentUploadForm()

    return render(
        request,
        'travel_app/client/upload_document.html',
        {
            'form': form,
            'client': client
        }
    )

@login_required
def agent_register(request):
    """
    Admin-only agent/staff registration.
    """

    # Only existing administrators can create agents
    if not (
        request.user.is_superuser
        or request.user.role == 'admin'
    ):
        messages.error(
            request,
            'Only administrators can create agent accounts.'
        )
        return redirect('travel_app:dashboard')

    if request.method == 'POST':

        form = AgentRegistrationForm(request.POST)

        if form.is_valid():

            try:
                agent = form.save()

                messages.success(
                    request,
                    f'Agent account for {agent.get_full_name() or agent.username} '
                    f'was created successfully.'
                )

                return redirect(
                    'travel_app:dashboard'
                )

            except Exception as exc:
                logger.exception(
                    'Agent registration failed: %s',
                    exc
                )

                form.add_error(
                    None,
                    'We could not create the agent account. '
                    'Please check the information and try again.'
                )

    else:
        form = AgentRegistrationForm()

    return render(
        request,
        'travel_app/agent/register.html',
        {
            'form': form,
        }
    )

def custom_logout(request):
    user_role = getattr(request.user, 'role', None)

    logout(request)

    if user_role == 'client':
        return redirect('travel_app:client_login')

    return redirect('travel_app:admin_login')

def landing_page(request):
    return render(request, 'travel_app/landing.html')
