from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from travel_app.models import Agent, Client, TravelPackage, Booking, Document, Payment
import random

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('📦 Creating sample data...')
        
        # 1. Create admin user if not exists
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
        
        # 2. Create packages
        packages_data = [
            {
                'name': 'Hajj 2026 Premium Package',
                'package_type': 'hajj_2024',
                'description': '5-star Hajj package with VIP services',
                'price': 8500.00,
                'duration_days': 14,
                'available_from': '2026-01-01',
                'available_until': '2027-12-31',
            },
            {
                'name': 'Umrah Luxury Package',
                'package_type': 'umrah',
                'description': '5-star Umrah package with VIP services',
                'price': 4200.00,
                'duration_days': 10,
                'available_from':'2026-01-01',
                'available_until': '2027-12-31',
            },
            {
                'name': 'UK Student Visa Package',
                'package_type': 'student_visa_uk',
                'description': 'Complete UK Student Visa application support',
                'price': 1200.00,
                'duration_days': 0,
                'available_from': '2024-01-01',
                'available_until': '2024-12-31',
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
            self.stdout.write(f'✅ Created package: {pkg.name}')
        
        # 3. Create clients
        clients_data = [
            {'first_name': 'Ahmed', 'last_name': 'Al-Farsi', 'passport': 'A12345678', 'email': 'ahmed@email.com', 'phone': '+966501234567', 'travel_type': 'hajj'},
            {'first_name': 'Fatima', 'last_name': 'Rashid', 'passport': 'R56789012', 'email': 'fatima@email.com', 'phone': '+971501234567', 'travel_type': 'umrah'},
            {'first_name': 'Mohammed', 'last_name': 'Khan', 'passport': 'K98765432', 'email': 'mohammed@email.com', 'phone': '+923001234567', 'travel_type': 'hajj'},
            {'first_name': 'Samantha', 'last_name': 'Reed', 'passport': 'R34567890', 'email': 'samantha@email.com', 'phone': '+447712345678', 'travel_type': 'visa_student'},
            {'first_name': 'Yusuf', 'last_name': 'Ibrahim', 'passport': 'I23456789', 'email': 'yusuf@email.com', 'phone': '+905301234567', 'travel_type': 'umrah'},
        ]
        
        clients = []
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                passport_number=client_data['passport'],
                defaults={
                    'first_name': client_data['first_name'],
                    'last_name': client_data['last_name'],
                    'passport_expiry': '2026-12-31',
                    'nationality': 'Saudi Arabia',
                    'date_of_birth': '1980-01-01',
                    'email': client_data['email'],
                    'phone': client_data['phone'],
                    'travel_type': client_data['travel_type'],
                }
            )
            clients.append(client)
            self.stdout.write(f'✅ Created client: {client.first_name} {client.last_name}')
        
        # 4. Create bookings
for i, client in enumerate(clients[:3]):

    package = packages[i % len(packages)]

    booking, created = Booking.objects.get_or_create(
        client=client,
        package=package,
        defaults={
            'agent': admin,
            'status': 'confirmed' if i % 2 == 0 else 'pending',
            'total_amount': package.price,
            'paid_amount': package.price if i % 2 == 0 else 0,
            'payment_status': 'paid' if i % 2 == 0 else 'pending',
            'travel_date_start': (
                timezone.now().date()
                + timedelta(days=30 + i * 10)
            ),
            'travel_date_end': (
                timezone.now().date()
                + timedelta(days=30 + i * 10 + 14)
            ),
            'special_requests': (
                'Vegetarian meals' if i == 0 else ''
            ),
        }
    )

    if created:
        self.stdout.write(
            f'✅ Created booking: {booking.booking_id}'
        )
    else:
        self.stdout.write(
            f'ℹ️ Booking already exists: {booking.booking_id}'
        )
        self.stdout.write(f'📊 Total: {Client.objects.count()} clients, {Booking.objects.count()} bookings, {TravelPackage.objects.count()} packages')
