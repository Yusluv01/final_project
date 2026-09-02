import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords
from django.conf import settings


class Agent(AbstractUser):
    """Unified User Model for Admins, Staff and Clients."""

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
        ('client', 'Client'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client'
    )

    phone = PhoneNumberField(
        null=True,
        blank=True,
        region='NG'
    )

    agent_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to='agents/',
        null=True,
        blank=True
    )

    bio = models.TextField(
        null=True,
        blank=True
    )

    is_online = models.BooleanField(default=False)

    last_activity = models.DateTimeField(
        null=True,
        blank=True
    )

    passport_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    passport_expiry = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    address = models.TextField(
        null=True,
        blank=True
    )

    city = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    nationality = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    travel_type = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    next_of_kin_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    first_login = models.BooleanField(
        default=True
    )

    # Prevent reverse accessor clashes with Django's auth models
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='agent_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='agent_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def save(self, *args, **kwargs):

        if self.role in ['admin', 'staff'] and not self.agent_id:

            last_agent = (
                self.__class__
                .objects
                .exclude(agent_id__isnull=True)
                .exclude(agent_id='')
                .order_by('-agent_id')
                .first()
            )

            if last_agent and last_agent.agent_id:
                try:
                    last_num = int(
                        last_agent.agent_id.split('-')[1]
                    )
                    new_num = last_num + 1

                except (IndexError, ValueError):
                    new_num = 1

            else:
                new_num = 1

            while True:

                new_id = f"TB-{str(new_num).zfill(4)}"

                if not self.__class__.objects.filter(
                    agent_id=new_id
                ).exists():

                    self.agent_id = new_id
                    break

                new_num += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    @property
    def is_client(self):
        return self.role == 'client'

    @property
    def is_staff_member(self):
        return self.role in ['admin', 'staff']


# ============================================================
# AGENT INVITATION
# ============================================================
class AgentInvitation(models.Model):
    """
    Invitation sent by an administrator to create
    an Admin or Staff account.
    """

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
    ]

    email = models.EmailField()

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    invited_by = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    accepted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    is_accepted = models.BooleanField(
        default=False
    )

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def is_valid(self):
        return (
            not self.is_accepted
            and not self.is_expired()
        )

    def __str__(self):
        return f"{self.email} - {self.get_role_display()}"

# ============================================================
# TRAVEL PACKAGE
# ============================================================

class TravelPackage(models.Model):
    """Travel package details."""

    PACKAGE_TYPE = [
        ('hajj_2024', 'Hajj 2024'),
        ('hajj_2025', 'Hajj 2025'),
        ('umrah', 'Umrah'),
        ('umrah_ramadan', 'Umrah - Ramadan'),
        ('umrah_regular', 'Umrah - Regular'),
        ('student_visa_uk', 'Student Visa - UK'),
        ('student_visa_canada', 'Student Visa - Canada'),
        ('tourist_visa', 'Tourist Visa'),
        ('business_visa', 'Business Visa'),
        ('family_visit', 'Family Visit Visa'),
        ('custom', 'Custom Package'),
    ]

    name = models.CharField(max_length=200)

    package_type = models.CharField(
        max_length=20,
        choices=PACKAGE_TYPE
    )

    description = models.TextField()

    short_description = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    duration_days = models.IntegerField(
        default=0
    )

    includes = models.JSONField(
        default=list,
        blank=True
    )

    excludes = models.JSONField(
        default=list,
        blank=True
    )

    requirements = models.JSONField(
        default=list,
        blank=True
    )

    featured_image = models.ImageField(
        upload_to='packages/',
        null=True,
        blank=True
    )

    available_from = models.DateField()

    available_until = models.DateField()

    is_active = models.BooleanField(
        default=True
    )

    is_featured = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    destination = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    def __str__(self):
        return (
            f"{self.name} - "
            f"{self.get_package_type_display()}"
        )


# ============================================================
# CLIENT
# ============================================================

class Client(models.Model):
    """Client model for tracking travelers."""

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='client_profile'
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=20
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    passport_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    passport_expiry = models.DateField(
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    nationality = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    TRAVEL_TYPE_CHOICES = [
        ('hajj', 'Hajj'),
        ('umrah', 'Umrah'),
        ('visa_student', 'Student Visa'),
        ('visa_tourist', 'Tourist Visa'),
        ('other', 'Other'),
    ]

    travel_type = models.CharField(
        max_length=20,
        choices=TRAVEL_TYPE_CHOICES,
        default='umrah'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['-created_at']


# ============================================================
# CLIENT DOCUMENT
# ============================================================

class ClientDocument(models.Model):
    """Documents uploaded by clients themselves."""

    DOCUMENT_TYPES = [
        ('passport', 'Passport Copy'),
        ('passport_photo', 'Passport Photograph'),
        ('visa', 'Visa Copy'),
        ('id_card', 'ID Card'),
        ('vaccination', 'Vaccination Certificate'),
        ('other', 'Other'),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to='documents/'
    )

    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default='other'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    is_rejected = models.BooleanField(
        default=False
    )

    verified_by = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.client.full_name} - "
            f"{self.get_document_type_display()}"
        )

# ============================================================
# BOOKING
# ============================================================

class Booking(models.Model):
    """Booking/Itinerary model."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Documents'),
        ('processing', 'Processing'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    TRAVEL_CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('premium_economy', 'Premium Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]

    booking_id = models.CharField(
        max_length=20,
        unique=True
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    package = models.ForeignKey(
        TravelPackage,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bookings'
    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bookings'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    travel_class = models.CharField(
        max_length=20,
        choices=TRAVEL_CLASS_CHOICES,
        default='economy'
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('partial', 'Partial'),
            ('refunded', 'Refunded')
        ],
        default='pending'
    )

    travel_date_start = models.DateField()

    travel_date_end = models.DateField()

    flight_details = models.JSONField(
        default=dict,
        null=True,
        blank=True
    )

    hotel_details = models.JSONField(
        default=dict,
        null=True,
        blank=True
    )

    transport_details = models.JSONField(
        default=dict,
        null=True,
        blank=True
    )

    special_requests = models.TextField(
        null=True,
        blank=True
    )

    document_metadata = models.JSONField(
        default=dict,
        null=True,
        blank=True
    )

    cancellation_policy = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    itinerary_details = models.TextField(
        null=True,
        blank=True
    )

    history = HistoricalRecords()

    # ============================================================
    # SAVE
    # ============================================================

    def save(self, *args, **kwargs):

        if not self.booking_id:

            year_month = timezone.now().strftime('%Y%m')

            # Find existing booking IDs for this month
            existing_ids = (
                Booking.objects
                .filter(
                    booking_id__startswith=f'TB-{year_month}-'
                )
                .values_list(
                    'booking_id',
                    flat=True
                )
            )

            highest_number = 0

            for existing_id in existing_ids:

                try:
                    number = int(
                        existing_id.split('-')[-1]
                    )

                    highest_number = max(
                        highest_number,
                        number
                    )

                except (ValueError, IndexError):
                    continue

            # Generate next booking number
            next_number = highest_number + 1

            self.booking_id = (
                f'TB-{year_month}-'
                f'{str(next_number).zfill(4)}'
            )

        super().save(*args, **kwargs)

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"{self.booking_id} - "
            f"{self.client.first_name} "
            f"{self.client.last_name}"
        )

    # ============================================================
    # BALANCE DUE
    # ============================================================

    @property
    def balance_due(self):

        balance = (
            self.total_amount
            - self.paid_amount
            - self.discount_amount
        )

        # Never return a negative balance
        return max(balance, 0)

    # ============================================================
    # CAN PAY
    # ============================================================

    @property
    def can_pay(self):
        """
        Return True when the booking has an outstanding balance
        and is not cancelled or refunded.
        """

        return (
            self.balance_due > 0
            and self.status not in (
                'cancelled',
                'refunded'
            )
            and self.payment_status != 'paid'
        )


# ============================================================
# DOCUMENT
# ============================================================

class Document(models.Model):
    """Document tracking for clients."""

    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('passport_photo', 'Passport Photo'),
        ('visa', 'Visa'),
        ('visa_application', 'Visa Application Form'),
        ('vaccination', 'Vaccination Certificate'),
        ('bank_statement', 'Bank Statement'),
        ('enrollment_letter', 'Enrollment Letter'),
        ('medical_report', 'Medical Report'),
        ('travel_insurance', 'Travel Insurance'),
        ('flight_ticket', 'Flight Ticket'),
        ('hotel_voucher', 'Hotel Voucher'),
        ('consent_form', 'Consent Form'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Upload'),
        ('uploaded', 'Uploaded'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='uploaded_documents'
    )

    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES
    )

    file = models.FileField(
        upload_to='documents/%Y/%m/%d/',
        null=True,
        blank=True
    )

    file_name = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    file_size = models.IntegerField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    verified_by = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    verification_date = models.DateTimeField(
        null=True,
        blank=True
    )

    verification_notes = models.TextField(
        null=True,
        blank=True
    )

    expiry_date = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        null=True,
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.booking.booking_id} - "
            f"{self.get_document_type_display()}"
        )


# ============================================================
# MESSAGE
# ============================================================

class Message(models.Model):
    """Messaging center model."""

    MESSAGE_TYPES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('system', 'System Notification'),
        ('in_app', 'In-App Message'),
    ]

    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,
        blank=True
    )

    sender = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_messages'
    )

    recipient = models.CharField(
        max_length=100
    )

    recipient_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='whatsapp'
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )

    subject = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    content = models.TextField()

    is_bulk = models.BooleanField(
        default=False
    )

    template_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    attachment = models.FileField(
        upload_to='messages/',
        null=True,
        blank=True
    )

    sent_at = models.DateTimeField(
        auto_now_add=True
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
            ('delivered', 'Delivered'),
            ('read', 'Read')
        ],
        default='pending'
    )

    error_message = models.TextField(
        null=True,
        blank=True
    )

    metadata = models.JSONField(
        default=dict,
        null=True,
        blank=True
    )

    history = HistoricalRecords()

    def __str__(self):
        return (
            f"{self.booking.booking_id if self.booking else 'Bulk'} "
            f"- {self.message_type}"
        )


# ============================================================
# PAYMENT
# ============================================================

class Payment(models.Model):
    """Payment tracking model."""

    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('paystack', 'Paystack'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('chargeback', 'Chargeback'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    invoice_number = models.CharField(
        max_length=20,
        unique=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )

    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    payment_gateway_response = models.JSONField(
        default=dict,
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    refunded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    refund_reason = models.TextField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.invoice_number:
            self.invoice_number = (
                f"INV-{timezone.now().strftime('%Y%m')}-"
                f"{str(self.id or 1).zfill(4)}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.amount}"


# ============================================================
# NOTIFICATION
# ============================================================

class Notification(models.Model):
    """System notifications."""

    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('reminder', 'Reminder'),
        ('alert', 'Alert'),
    ]

    recipient = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='info'
    )

    link = models.URLField(
        null=True,
        blank=True
    )

    link_text = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    is_read = models.BooleanField(
        default=False
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def mark_as_read(self):

        if not self.is_read:

            self.is_read = True
            self.read_at = timezone.now()

            self.save(
                update_fields=[
                    'is_read',
                    'read_at'
                ]
            )

    def __str__(self):
        return (
            f"{self.title} - "
            f"{self.recipient.username}"
        )


# ============================================================
# AUDIT LOG
# ============================================================

class AuditLog(models.Model):
    """Audit log for tracking changes."""

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]

    user = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )

    model_name = models.CharField(
        max_length=100
    )

    object_id = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    object_repr = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    changes = models.JSONField(
        default=dict,
        null=True,
        blank=True
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.user} - "
            f"{self.action} - "
            f"{self.model_name}"
        )


# ============================================================
# FLIGHT SEARCH HISTORY
# ============================================================

class FlightSearchHistory(models.Model):
    """Track flight searches for analytics."""

    user = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='flight_searches'
    )

    origin = models.CharField(
        max_length=10
    )

    destination = models.CharField(
        max_length=10
    )

    departure_date = models.DateField()

    return_date = models.DateField(
        null=True,
        blank=True
    )

    passengers = models.IntegerField(
        default=1
    )

    travel_class = models.CharField(
        max_length=20,
        default='economy'
    )

    results_count = models.IntegerField(
        default=0
    )

    searched_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.origin} → {self.destination} - "
            f"{self.searched_at.strftime('%Y-%m-%d')}"
        )


# ============================================================
# FLIGHT
# ============================================================

class Flight(models.Model):
    """
    Stores individual flight search results so that users can
    open a flight and view its full Travelbolt intelligence.
    """

    flight_id = models.CharField(
        max_length=50,
        unique=True
    )

    airline = models.CharField(
        max_length=100
    )

    origin = models.CharField(
        max_length=10
    )

    destination = models.CharField(
        max_length=10
    )

    departure_date = models.DateField(
        null=True,
        blank=True
    )

    departure = models.CharField(
        max_length=100
    )

    arrival = models.CharField(
        max_length=100
    )

    duration = models.CharField(
        max_length=50
    )

    stops = models.IntegerField(
        default=0
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    service_score = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )

    punctuality_score = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )

    comfort_score = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )

    transit_score = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )

    historical_summary = models.TextField(
        blank=True,
        null=True
    )

    strengths = models.JSONField(
        default=list,
        blank=True
    )

    concerns = models.JSONField(
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.flight_id} - "
            f"{self.airline} - "
            f"{self.origin} → {self.destination}"
        )

    class Meta:
        ordering = ['price']
