from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from travel_app.models import (
    Agent,
    Client,
    TravelPackage,
    Booking,
)


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):

        self.stdout.write('📦 Creating sample data...')

        # ============================================================
        # 1. CREATE ADMIN USER
        # ============================================================

        admin, created = Agent.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@travelbolt.ai',
                'is_staff': True,
                'is_superuser': True,
            }
        )

        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('✅ Admin user created')
        else:
            self.stdout.write('✅ Admin user already exists')


        # ============================================================
        # 2. CREATE TRAVEL PACKAGES
        # ============================================================

        packages_data = [

            {
                'name': 'Hajj 2026 Premium Package',
                'package_type': 'hajj_2025',
                'description': 'Premium Hajj package with VIP services.',
                'price': 8500000.00,
                'duration_days': 14,
                'available_from': '2026-01-01',
                'available_until': '2026-12-31',
            },

            {
                'name': 'Umrah Luxury Package',
                'package_type': 'umrah',
                'description': 'Luxury Umrah package with premium accommodation and services.',
                'price': 4200000.00,
                'duration_days': 10,
                'available_from': '2026-01-01',
                'available_until': '2026-12-31',
            },

            {
                'name': 'Umrah Ramadan Package',
                'package_type': 'umrah_ramadan',
                'description': 'Special Ramadan Umrah package.',
                'price': 5000000.00,
                'duration_days': 14,
                'available_from': '2026-01-01',
                'available_until': '2026-12-31',
            },

            {
                'name': 'UK Student Visa Package',
                'package_type': 'student_visa_uk',
                'description': 'Complete UK Student Visa application support.',
                'price': 1200000.00,
                'duration_days': 0,
                'available_from': '2026-01-01',
                'available_until': '2026-12-31',
            },

            {
                'name': 'Canada Student Visa Package',
                'package_type': 'student_visa_canada',
                'description': 'Complete Canada Student Visa application support.',
                'price': 1500000.00,
                'duration_days': 0,
                'available_from': '2026-01-01',
                'available_until': '2026-12-31',
            },

        ]

        packages = []

        for pkg_data in packages_data:

            pkg, created = TravelPackage.objects.get_or_create(
                name=pkg_data['name'],
                defaults={
                    'package_type': pkg_data['package_type'],
                    'description': pkg_data['description'],
                    'price': pkg_data['price'],
                    'duration_days': pkg_data['duration_days'],
                    'available_from': pkg_data['available_from'],
                    'available_until': pkg_data['available_until'],
                    'is_active': True,
                    'is_featured': True,
                }
            )

            packages.append(pkg)

            self.stdout.write(
                f'✅ {"Created" if created else "Found"} package: {pkg.name}'
            )


        # ============================================================
        # 3. CREATE SAMPLE CLIENTS
        # ============================================================

        clients_data = [

            {
                'first_name': 'Ahmed',
                'last_name': 'Al-Farsi',
                'passport': 'A12345678',
                'email': 'ahmed@email.com',
                'phone': '+966501234567',
                'travel_type': 'hajj',
            },

            {
                'first_name': 'Fatima',
                'last_name': 'Rashid',
                'passport': 'R56789012',
                'email': 'fatima@email.com',
                'phone': '+971501234567',
                'travel_type': 'umrah',
            },

            {
                'first_name': 'Mohammed',
                'last_name': 'Khan',
                'passport': 'K98765432',
                'email': 'mohammed@email.com',
                'phone': '+923001234567',
                'travel_type': 'hajj',
            },

            {
                'first_name': 'Samantha',
                'last_name': 'Reed',
                'passport': 'R34567890',
                'email': 'samantha@email.com',
                'phone': '+447712345678',
                'travel_type': 'visa_student',
            },

            {
                'first_name': 'Yusuf',
                'last_name': 'Ibrahim',
                'passport': 'I23456789',
                'email': 'yusuf@email.com',
                'phone': '+905301234567',
                'travel_type': 'umrah',
            },

        ]

        clients = []

        for client_data in clients_data:

            client, created = Client.objects.get_or_create(
                passport_number=client_data['passport'],
                defaults={
                    'first_name': client_data['first_name'],
                    'last_name': client_data['last_name'],
                    'passport_expiry': '2026-12-31',
                    'nationality': 'Nigeria',
                    'date_of_birth': '1980-01-01',
                    'email': client_data['email'],
                    'phone': client_data['phone'],
                    'travel_type': client_data['travel_type'],
                }
            )

            clients.append(client)

            self.stdout.write(
                f'✅ {"Created" if created else "Found"} client: '
                f'{client.first_name} {client.last_name}'
            )


        # ============================================================
        # 4. CREATE SAMPLE BOOKINGS
        # ============================================================

        for i, client in enumerate(clients[:3]):

            package = packages[i % len(packages)]

            booking = Booking.objects.create(

                client=client,

                package=package,

                agent=admin,

                status='confirmed' if i % 2 == 0 else 'pending',

                total_amount=package.price,

                paid_amount=(
                    package.price
                    if i % 2 == 0
                    else 0
                ),

                payment_status=(
                    'paid'
                    if i % 2 == 0
                    else 'pending'
                ),

                travel_date_start=(
                    timezone.now().date()
                    + timedelta(days=30 + i * 10)
                ),

                travel_date_end=(
                    timezone.now().date()
                    + timedelta(days=44 + i * 10)
                ),

                special_requests=(
                    'Vegetarian meals'
                    if i == 0
                    else ''
                ),
            )

            self.stdout.write(
                f'✅ Created booking: {booking.booking_id}'
            )


        # ============================================================
        # 5. SUMMARY
        # ============================================================

        self.stdout.write(
            self.style.SUCCESS(
                '🎉 Sample data created successfully!'
            )
        )

        self.stdout.write(
            f'📊 Total: '
            f'{Client.objects.count()} clients, '
            f'{Booking.objects.count()} bookings, '
            f'{TravelPackage.objects.count()} packages'
        )
