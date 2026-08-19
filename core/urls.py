from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('travel_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)





# core/urls.py
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib.auth import views as auth_views
# from travel_app import views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('travel_app.urls')),
    
#     # ADD THESE LINES - This creates a global 'login' URL name
#     path('login/', auth_views.LoginView.as_view(template_name='travel_app/auth/login.html'), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
#         # Client Portal
#     path('client/register/', views.client_register, name='client_register'),
#     path('client/login/', views.custom_client_login, name='client_login'),
#     path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
#     path('client/logout/', views.client_logout, name='client_logout'),
#     path('client/flight-search/', views.client_flight_search, name='client_flight_search'),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # import debug_toolbar
    # urlpatterns += [
    # #     path('__debug__/', include(debug_toolbar.urls)),

    # ]