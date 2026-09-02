from django.urls import path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from . import views



app_name = 'travel_app'


urlpatterns = [

    # ============================================================
    # DASHBOARD & LANDING
    # ============================================================

    path(
        '',
        views.landing_page,
        name='landing_page'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    


    # ============================================================
    # AUTHENTICATION
    # ============================================================

    path(
        'logout/',
        views.custom_logout,
        name='logout'
    ),

    path(
        'agency-secure-login-2026/',
        views.admin_login,
        name='admin_login'
    ),

    # ============================================================
# ADMIN / STAFF PASSWORD RESET
# ============================================================

path(
    'password-reset/',
    auth_views.PasswordResetView.as_view(
        template_name='travel_app/auth/admin_password_reset.html',
        email_template_name='travel_app/auth/admin_password_reset_email.html',
        subject_template_name='travel_app/auth/admin_password_reset_subject.txt',
        success_url='/password-reset/done/'
    ),
    name='password_reset'
),

path(
    'password-reset/done/',
    auth_views.PasswordResetDoneView.as_view(
        template_name='travel_app/auth/admin_password_reset_done.html'
    ),
    name='password_reset_done'
),

path(
    'password-reset/confirm/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='travel_app/auth/admin_password_reset_confirm.html',
        success_url='/password-reset/complete/'
    ),
    name='password_reset_confirm'
),

path(
    'password-reset/complete/',
    auth_views.PasswordResetCompleteView.as_view(
        template_name='travel_app/auth/admin_password_reset_complete.html'
    ),
    name='password_reset_complete'
),


    # ============================================================
    # EXPORT REPORT
    # ============================================================

    path(
        'export-report/',
        views.export_report,
        name='export_report'
    ),


    # ============================================================
    # ADMIN CLIENT MANAGEMENT
    # ============================================================

    path(
        'clients/',
        views.ClientListView.as_view(),
        name='clients'
    ),

    path(
        'clients/<int:pk>/',
        views.ClientDetailView.as_view(),
        name='client_detail'
    ),

    path(
        'clients/create/',
        views.ClientCreateView.as_view(),
        name='client_create'
    ),

    path(
        'clients/<int:pk>/edit/',
        views.ClientUpdateView.as_view(),
        name='client_edit'
    ),

    path(
        'clients/<int:pk>/delete/',
        views.ClientDeleteView.as_view(),
        name='client_delete'
    ),


    # ============================================================
    # ITINERARIES
    # ============================================================

    path(
        'itineraries/',
        views.ItineraryListView.as_view(),
        name='itineraries'
    ),

    path(
        'itineraries/<int:pk>/',
        views.ItineraryDetailView.as_view(),
        name='itinerary_detail'
    ),

    path(
        'itineraries/create/',
        views.ItineraryCreateView.as_view(),
        name='itinerary_create'
    ),

    path(
        'itineraries/<int:pk>/save/',
        views.itinerary_save,
        name='itinerary_save'
    ),

    path(
        'itineraries/<int:pk>/export-pdf/',
        views.itinerary_export_pdf,
        name='itinerary_export_pdf'
    ),

    path(
        'itineraries/<int:pk>/share/',
        views.itinerary_share,
        name='itinerary_share'
    ),


    # ============================================================
    # ADMIN PAYMENTS
    # ============================================================

    path(
        'payments/',
        login_required(views.PaymentView.as_view()),
        name='payments'
    ),

    path(
        'payments/success/',
        views.client_payment_success,
        name='payment_success'
    ),

    path(
        'payments/process/',
        views.process_payment,
        name='process_payment'
    ),


    # ============================================================
    # ADMIN MESSAGING
    # ============================================================

    path(
        'messages/',
        views.MessagingView.as_view(),
        name='messages'
    ),

    path(
        'messages/send/',
        views.send_message,
        name='send_message'
    ),


    # ============================================================
    # FLIGHT SEARCH
    # ============================================================

    path(
        'search/',
        views.flight_search,
        name='flight_search'
    ),
    
    path(
    'flight/details/<str:flight_id>/',
    views.flight_details,
    name='flight_details'
),

    path(
        'api/flights/search/',
        views.flight_search_api,
        name='flight_search_api'
    ),


    # ============================================================
    # EXPLORE
    # ============================================================

    path(
        'explore/',
        views.explore,
        name='explore'
    ),


    # ============================================================
    # AI ASSISTANT
    # ============================================================

    path(
        'api/ai-assistant/',
        views.ai_assistant_chat,
        name='ai_assistant_chat'
    ),

    path(
        'test-ai/',
        views.test_ai,
        name='test_ai'
    ),


    # ============================================================
    # CLIENT PORTAL
    # ============================================================

    path(
        'client/login/',
    views.client_login,
    name='client_login'
),

path(
    'client/register/',
    views.client_register,
    name='client_register'
),

path(
    'client/dashboard/',
    views.client_dashboard,
    name='client_dashboard'
),

path(
    'client/profile/',
    views.client_profile,
    name='client_profile'
),

path(
    'client/ai-assistant/',
    views.client_ai_assistant,
    name='client_ai_assistant'
),

path(
    'client/documents/',
    views.client_documents,
    name='client_documents'
),

path(
    'client/logout/',
    views.client_logout,
    name='client_logout'
),

# ============================================================
# CLIENT PASSWORD RESET
# ============================================================

path(
    'client/password-reset/',
    views.ClientPasswordResetView.as_view(),
    name='client_password_reset'
),

path(
    'client/password-reset/done/',
    views.ClientPasswordResetDoneView.as_view(),
    name='client_password_reset_done'
),

path(
    'client/password-reset/confirm/<uidb64>/<token>/',
    views.ClientPasswordResetConfirmView.as_view(),
    name='client_password_reset_confirm'
),

path(
    'client/password-reset/complete/',
    views.ClientPasswordResetCompleteView.as_view(),
    name='client_password_reset_complete'
),
path(
    'client/upload-document/',
    views.client_upload_document,
    name='client_upload_document'
),

    # ============================================================
    # CLIENT PAYMENTS
    # ============================================================

    path(
        'client/payments/',
        views.client_payments,
        name='client_payments'
    ),

    path(
        'client/payment-success/',
        views.client_payment_success,
        name='client_payment_success'
    ),


    # ============================================================
    # MAGIC LOGIN
    # TESTING ONLY
    # ============================================================

    # path(
    #     'client/magic-login/<str:username>/',
    #     views.magic_client_login,
    #     name='magic_client_login'
    # ),


    # ============================================================
    # DOCUMENTS
    # ============================================================

    path(
        'admin-view-document/<int:doc_id>/',
        views.admin_view_document,
        name='admin_view_document'
    ),

    path(
    'admin-download-document/<int:doc_id>/',
    views.admin_download_document,
    name='admin_download_document'
),

path(
    'admin-approve-document/<int:doc_id>/',
    views.admin_approve_document,
    name='admin_approve_document'
),

path(
    'admin-reject-document/<int:doc_id>/',
    views.admin_reject_document,
    name='admin_reject_document'
),
path(
    'agent/register/',
    views.agent_register,
    name='agent_register'
),

path(
    'agent/invite/<uuid:token>/',
    views.accept_agent_invitation,
    name='accept_agent_invitation'
),

path(
    'logout/',
    views.custom_logout,
    name='logout'
),

path(
    'client/booking/<int:booking_id>/pay/',
    views.pay_booking,
    name='pay_booking'
),

path(
    'payment/paystack/callback/',
    views.paystack_callback,
    name='paystack_callback'
),

    path(
    'notifications/',
    views.notifications,
    name='notifications'
),

path(
    'notifications/<int:notification_id>/read/',
    views.mark_notification_read,
    name='mark_notification_read'
),

path(
    'notifications/mark-all-read/',
    views.mark_all_notifications_read,
    name='mark_all_notifications_read'
),

    
    # =========================================================
    # CLIENT TRAVEL PACKAGES
    # =========================================================

    path(
        'client/packages/',
        views.client_packages,
        name='client_packages'
    ),

    path(
        'client/packages/<int:pk>/',
        views.client_package_detail,
        name='client_package_detail'
    ),

    path(
        'client/packages/<int:pk>/select/',
        views.select_package,
        name='select_package'
    ),

    # =========================================================
    # CLIENT BOOKING 
    # =========================================================

    path(
    'client/bookings/',
    views.client_bookings,
    name='client_bookings'
),

    path(
        'client/bookings/<int:pk>/',
        views.client_booking_detail,
        name='client_booking_detail'
    ),

]

































