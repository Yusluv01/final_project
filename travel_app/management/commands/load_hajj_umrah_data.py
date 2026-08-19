# travel_app/management/commands/load_hajj_umrah_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from travel_app.models import (
    Agent, Client, TravelPackage, Booking, 
    Document, Payment, Notification
)
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Load Hajj and Umrah sample data'

    def handle(self, *args, **options):
        self.stdout.write('Loading Hajj and Umrah data...')
        
        # Create packages
        self.create_packages()
        
        # Create clients
        self.create_clients()
        
        # Create bookings
        self.create_bookings()
        
        self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))
    
    def create_packages(self):
        """Create Hajj and Umrah packages"""
        
        packages_data = [
            # ==================== HAJJ PACKAGES ====================
            {
                'name': 'Hajj 2024 - Premium Package',
                'package_type': 'hajj_2024',
                'description': 'Complete Hajj package with 5-star accommodation in Makkah and Madinah. Includes VIP transportation, guided rituals, and full support.',
                'short_description': '5-star Hajj package with VIP services',
                'price': 8500.00,
                'duration_days': 14,
                'includes': [
                    '5-star hotel in Makkah (10 nights)',
                    '5-star hotel in Madinah (4 nights)',
                    'Private VIP transportation',
                    'Expert Hajj guide (English/Arabic)',
                    'All meals (breakfast, lunch, dinner)',
                    'Zamzam water package',
                    'Hajj kit (Ihram, prayer mat, etc.)',
                    '24/7 medical support',
                    'Visa processing assistance',
                    'Flight tickets (round trip)',
                ],
                'excludes': [
                    'Personal expenses',
                    'Additional shopping',
                    'Travel insurance (optional)',
                ],
                'requirements': [
                    'Valid passport (6+ months validity)',
                    'Meningitis ACWY vaccination',
                    'Hajj visa',
                    'Medical fitness certificate',
                    'Proof of relationship for women (Mahram)',
                ],
                'available_from': '2024-05-01',
                'available_until': '2024-06-15',
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Hajj 2024 - Standard Package',
                'package_type': 'hajj_2024',
                'description': 'Comfortable Hajj package with 4-star accommodation. Includes group transportation and guided rituals.',
                'short_description': '4-star Hajj package with group services',
                'price': 5500.00,
                'duration_days': 14,
                'includes': [
                    '4-star hotel in Makkah (10 nights)',
                    '4-star hotel in Madinah (4 nights)',
                    'Group transportation',
                    'Hajj guide (Arabic/English)',
                    'All meals (breakfast, lunch, dinner)',
                    'Hajj kit (Ihram, prayer mat)',
                    'Medical support',
                    'Visa processing assistance',
                    'Flight tickets (round trip)',
                ],
                'excludes': [
                    'Personal expenses',
                    'Shopping',
                    'Travel insurance',
                ],
                'requirements': [
                    'Valid passport (6+ months validity)',
                    'Meningitis ACWY vaccination',
                    'Hajj visa',
                    'Medical fitness certificate',
                ],
                'available_from': '2024-05-01',
                'available_until': '2024-06-15',
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Hajj 2024 - Economy Package',
                'package_type': 'hajj_2024',
                'description': 'Affordable Hajj package with 3-star accommodation. Basic services for budget-conscious pilgrims.',
                'short_description': 'Budget Hajj package',
                'price': 3500.00,
                'duration_days': 14,
                'includes': [
                    '3-star hotel in Makkah (10 nights)',
                    '3-star hotel in Madinah (4 nights)',
                    'Group transportation',
                    'Basic Hajj guidance',
                    'Meals (breakfast and dinner)',
                    'Hajj kit (Ihram)',
                    'Visa processing assistance',
                    'Flight tickets (round trip)',
                ],
                'excludes': [
                    'Personal expenses',
                    'Shopping',
                    'Travel insurance',
                    'Lunch meals',
                ],
                'requirements': [
                    'Valid passport (6+ months validity)',
                    'Meningitis ACWY vaccination',
                    'Hajj visa',
                    'Medical fitness certificate',
                ],
                'available_from': '2024-05-01',
                'available_until': '2024-06-15',
                'is_active': True,
                'is_featured': False,
            },
            
            # ==================== UMRAH PACKAGES ====================
            {
                'name': 'Umrah - Luxury Package',
                'package_type': 'umrah',
                'description': 'Premium Umrah experience with 5-star hotels close to Haram. VIP services throughout your journey.',
                'short_description': '5-star Umrah with VIP services',
                'price': 4200.00,
                'duration_days': 10,
                'includes': [
                    '5-star hotel in Makkah (7 nights) - Walking distance to Haram',
                    '5-star hotel in Madinah (3 nights) - Walking distance to Masjid Nabawi',
                    'Private VIP transportation',
                    'Expert Umrah guide',
                    'All meals (breakfast, lunch, dinner)',
                    'Zamzam water package',
                    'Umrah kit',
                    '24/7 concierge service',
                    'Visa processing',
                    'Flight tickets (round trip)',
                ],
                'excludes': [
                    'Personal expenses',
                    'Shopping',
                    'Travel insurance',
                ],
                'requirements': [
                    'Valid passport (6+ months validity)',
                    'Meningitis ACWY vaccination',
                    'Umrah visa',
                ],
                'available_from': '2024-01-01',
                'available_until': '2024-12-31',
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Umrah - Standard Package',
                'package_type': 'umrah',
                'description': 'Comfortable Umrah package with 4-star hotels. Group transportation and guided Umrah rituals.',
                'short_description': '4-star Umrah with group services',
                'price': 2800.00,
                'duration_days': 10,
                'includes': [
                    '4-star hotel in Makkah (7 nights)',
                    '4-star hotel in Madinah (3 nights)',
                    'Group transportation',
                    'Umrah guide (Arabic/English)',
                    'All meals (breakfast, dinner)',
                    'Umrah kit',
                    'Medical support',
                    'Visa processing',
                    'Flight tickets (round trip)',
                ],
                'excludes': [
                    'Personal expenses',
                    'Shopping',
                    'Travel insurance',
                    'Lunch meals',
                ],
                'requirements': [
                    'Valid passport (6+ months validity)',
                    'Meningitis ACWY vaccination',
                    'Umrah visa',
                ],
                'available_from': '2024-01-01',
                'available_until': '2024-12-31',
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Umrah - Economy Package',
                'package_type': 'umrah',
                'description': 'Affordable Umrah package with 3-star hotels. Basic services for budget travelers.',
                'short_description': 'Budget Umrah package',
                'price': 1800.00,
                'duration_days': 10,
                'includes': [
                    '3-star hotel in Makkah (7 nights)',
                    '3-star hotel in Madinah (3 nights)',
                    'Group transportation',
                    'Basic Umrah guidance',
                    'Meals (breakfast)',
                    'Umrah kit',
                    'Visa processing',
                    'Flight tickets (round trip)',
                ],
                'excludes': [
                    'Personal expenses',
                    'Shopping',
                    'Travel insurance',
                    'Dinner meals',
                    'Lunch meals',
                ],
                'requirements': [
                    'Valid passport (6+ months validity)',
                    'Meningitis ACWY vaccination',
                    'Umrah visa',
                ],
                'available_from': '2024-01-01',
                'available_until': '2024-12-31',
                'is_active': True,
                'is_featured': False,
            },
            
            # ==================== STUDENT VISA PACKAGES ====================
            {
                'name': 'UK Student Visa Package',
                'package_type': 'student_visa_uk',
                'description': 'Complete UK Student Visa application support including CAS, accommodation, and travel arrangements.',
                'short_description': 'UK Student Visa support',
                'price': 1200.00,
                'duration_days': 0,
                'includes': [
                    'CAS letter assistance',
                    'Visa application review',
                    'Accommodation booking',
                    'Flight booking assistance',
                    'Bank statement guidance',
                    'Interview preparation',
                    'Document verification',
                    'Travel insurance',
                ],
                'excludes': [
                    'Visa application fees',
                    'Tuition fees',
                    'Personal expenses',
                ],
                'requirements': [
                    'Valid passport (6+ months validity)',
                    'Offer letter from UK university',
                    'Financial proof',
                    'IELTS/English test scores',
                ],
                'available_from': '2024-01-01',
                'available_until': '2024-12-31',
                'is_active': True,
                'is_featured': False,
            },
            {
                'name': 'Canada Student Visa Package',
                'package_type': 'student_visa_canada',
                'description': 'Complete Canada Student Visa application support including study permit, accommodation, and travel.',
                'short_description': 'Canada Student Visa support',
                'price': 1400.00,
                'duration_days': 0,
                'includes': [
                    'Study permit assistance',
                    'Visa application review',
                    'Accommodation booking',
                    'Flight booking assistance',
                    'Bank statement guidance',
                    'Interview preparation',
                    'Document verification',
                    'Travel insurance',
                ],
                'excludes': [
                    'Visa application fees',
                    'Tuition fees',
                    'Personal expenses',
                ],
                'requirements': [
                    'Valid passport (6+ months validity)',
                    'Offer letter from Canadian university',
                    'Financial proof',
                    'IELTS/English test scores',
                ],
                'available_from': '2024-01-01',
                'available_until': '2024-12-31',
                'is_active': True,
                'is_featured': False,
            },
            
            # ==================== TOURIST VISA PACKAGES ====================
            {
                'name': 'UK Tourist Visa Package',
                'package_type': 'tourist_visa',
                'description': 'UK Tourist Visa application support including itinerary, accommodation, and travel arrangements.',
                'short_description': 'UK Tourist Visa support',
                'price': 450.00,
                'duration_days': 0,
                'includes': [
                    'Visa application review',
                    'Itinerary planning',
                    'Accommodation booking',
                    'Flight booking assistance',
                    'Document verification',
                    'Travel insurance',
                ],
                'excludes': [
                    'Visa application fees',
                    'Personal expenses',
                ],
                'requirements': [
                    'Valid passport (6+ months validity)',
                    'Financial proof',
                    'Travel itinerary',
                ],
                'available_from': '2024-01-01',
                'available_until': '2024-12-31',
                'is_active': True,
                'is_featured': False,
            },
            {
                'name': 'Saudi Tourist Visa Package',
                'package_type': 'tourist_visa',
                'description': 'Saudi Tourist Visa application support including e-visa, accommodation, and travel arrangements.',
                'short_description': 'Saudi Tourist Visa support',
                'price': 350.00,
                'duration_days': 0,
                'includes': [
                    'E-visa application assistance',
                    'Accommodation booking',
                    'Flight booking assistance',
                    'Document verification',
                    'Travel insurance',
                ],
                'excludes': [
                    'Visa application fees',
                    'Personal expenses',
                ],
                'requirements': [
                    'Valid passport (6+ months validity)',
                    'Financial proof',
                    'Travel itinerary',
                ],
                'available_from': '2024-01-01',
                'available_until': '2024-12-31',
                'is_active': True,
                'is_featured': False,
            },
        ]
        
        for pkg_data in packages_data:
            package, created = TravelPackage.objects.get_or_create(
                name=pkg_data['name'],
                defaults={
                    'package_type': pkg_data['package_type'],
                    'description': pkg_data['description'],
                    'short_description': pkg_data['short_description'],
                    'price': pkg_data['price'],
                    'duration_days': pkg_data['duration_days'],
                    'includes': pkg_data['includes'],
                    'excludes': pkg_data['excludes'],
                    'requirements': pkg_data['requirements'],
                    'available_from': pkg_data['available_from'],
                    'available_until': pkg_data['available_until'],
                    'is_active': pkg_data['is_active'],
                    'is_featured': pkg_data['is_featured'],
                }
            )
            if created:
                self.stdout.write(f' Created package: {package.name}')
            else:
                self.stdout.write(f'Package already exists: {package.name}')
    
    def create_clients(self):
        """Create sample clients"""
        
        clients_data = [
            {
                'first_name': 'Ahmed',
                'last_name': 'Al-Farsi',
                'gender': 'male',
                'passport_number': 'A12345678',
                'passport_expiry': '2025-12-31',
                'nationality': 'Saudi Arabia',
                'date_of_birth': '1980-06-15',
                'email': 'ahmed.alfarsi@email.com',
                'phone': '+966501234567',
                'travel_type': 'hajj',
            },
            {
                'first_name': 'Mohammed',
                'last_name': 'Khan',
                'gender': 'male',
                'passport_number': 'K98765432',
                'passport_expiry': '2026-08-20',
                'nationality': 'Pakistan',
                'date_of_birth': '1975-03-10',
                'email': 'mohammed.khan@email.com',
                'phone': '+923001234567',
                'travel_type': 'hajj',
            },
            {
                'first_name': 'Fatima',
                'last_name': 'Rashid',
                'gender': 'female',
                'passport_number': 'R56789012',
                'passport_expiry': '2025-11-30',
                'nationality': 'UAE',
                'date_of_birth': '1988-09-25',
                'email': 'fatima.rashid@email.com',
                'phone': '+971501234567',
                'travel_type': 'umrah',
            },
            {
                'first_name': 'Samantha',
                'last_name': 'Reed',
                'gender': 'female',
                'passport_number': 'R34567890',
                'passport_expiry': '2026-06-15',
                'nationality': 'United Kingdom',
                'date_of_birth': '2000-12-01',
                'email': 'samantha.reed@email.com',
                'phone': '+447712345678',
                'travel_type': 'visa_student',
            },
            {
                'first_name': 'Yusuf',
                'last_name': 'Ibrahim',
                'gender': 'male',
                'passport_number': 'I23456789',
                'passport_expiry': '2027-04-10',
                'nationality': 'Turkey',
                'date_of_birth': '1990-07-20',
                'email': 'yusuf.ibrahim@email.com',
                'phone': '+905301234567',
                'travel_type': 'umrah',
            },
            {
                'first_name': 'Zoya',
                'last_name': 'Malik',
                'gender': 'female',
                'passport_number': 'M87654321',
                'passport_expiry': '2026-09-30',
                'nationality': 'India',
                'date_of_birth': '1995-02-14',
                'email': 'zoya.malik@email.com',
                'phone': '+919871234567',
                'travel_type': 'visa_student',
            },
            {
                'first_name': 'Abdullah',
                'last_name': 'Omar',
                'gender': 'male',
                'passport_number': 'O45678901',
                'passport_expiry': '2025-07-25',
                'nationality': 'Egypt',
                'date_of_birth': '1983-11-05',
                'email': 'abdullah.omar@email.com',
                'phone': '+201001234567',
                'travel_type': 'hajj',
            },
            {
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'gender': 'female',
                'passport_number': 'G78901234',
                'passport_expiry': '2026-12-01',
                'nationality': 'Spain',
                'date_of_birth': '1992-04-08',
                'email': 'maria.garcia@email.com',
                'phone': '+346001234567',
                'travel_type': 'umrah',
            },
            {
                'first_name': 'Ali',
                'last_name': 'Hassan',
                'gender': 'male',
                'passport_number': 'H90123456',
                'passport_expiry': '2027-02-28',
                'nationality': 'Lebanon',
                'date_of_birth': '1978-08-12',
                'email': 'ali.hassan@email.com',
                'phone': '+96171234567',
                'travel_type': 'umrah',
            },
            {
                'first_name': 'Aisha',
                'last_name': 'Abdullah',
                'gender': 'female',
                'passport_number': 'A56789012',
                'passport_expiry': '2025-10-15',
                'nationality': 'Malaysia',
                'date_of_birth': '1986-05-18',
                'email': 'aisha.abdullah@email.com',
                'phone': '+60123456789',
                'travel_type': 'hajj',
            },
        ]
        
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                passport_number=client_data['passport_number'],
                defaults={
                    'first_name': client_data['first_name'],
                    'last_name': client_data['last_name'],
                    'gender': client_data['gender'],
                    'passport_expiry': client_data['passport_expiry'],
                    'nationality': client_data['nationality'],
                    'date_of_birth': client_data['date_of_birth'],
                    'email': client_data['email'],
                    'phone': client_data['phone'],
                    'travel_type': client_data['travel_type'],
                }
            )
            if created:
                self.stdout.write(f'✅ Created client: {client.first_name} {client.last_name}')
            else:
                self.stdout.write(f'⏩ Client already exists: {client.first_name} {client.last_name}')
    
    def create_bookings(self):
        """Create sample bookings"""
        
        # Get clients and packages
        clients = Client.objects.all()
        packages = TravelPackage.objects.filter(is_active=True)
        
        if not clients or not packages:
            self.stdout.write(self.style.WARNING('No clients or packages found. Skipping bookings.'))
            return
        
        # Create 5 sample bookings
        booking_data = [
            {
                'client': clients[0],  # Ahmed Al-Farsi
                'package': TravelPackage.objects.get(name='Hajj 2024 - Premium Package'),
                'status': 'confirmed',
                'travel_date_start': '2024-06-10',
                'travel_date_end': '2024-06-24',
                'total_amount': 8500.00,
                'paid_amount': 8500.00,
                'payment_status': 'paid',
                'special_requests': 'Need wheelchair assistance',
            },
            {
                'client': clients[1],  # Mohammed Khan
                'package': TravelPackage.objects.get(name='Hajj 2024 - Standard Package'),
                'status': 'pending',
                'travel_date_start': '2024-06-12',
                'travel_date_end': '2024-06-26',
                'total_amount': 5500.00,
                'paid_amount': 2000.00,
                'payment_status': 'partial',
                'special_requests': 'Vegetarian meals',
            },
            {
                'client': clients[2],  # Fatima Rashid
                'package': TravelPackage.objects.get(name='Umrah - Luxury Package'),
                'status': 'confirmed',
                'travel_date_start': '2024-03-15',
                'travel_date_end': '2024-03-25',
                'total_amount': 4200.00,
                'paid_amount': 4200.00,
                'payment_status': 'paid',
                'special_requests': '',
            },
            {
                'client': clients[3],  # Samantha Reed
                'package': TravelPackage.objects.get(name='UK Student Visa Package'),
                'status': 'processing',
                'travel_date_start': '2024-09-01',
                'travel_date_end': '2024-09-01',
                'total_amount': 1200.00,
                'paid_amount': 600.00,
                'payment_status': 'partial',
                'special_requests': 'Need accommodation near university',
            },
            {
                'client': clients[4],  # Yusuf Ibrahim
                'package': TravelPackage.objects.get(name='Umrah - Standard Package'),
                'status': 'completed',
                'travel_date_start': '2024-02-01',
                'travel_date_end': '2024-02-11',
                'total_amount': 2800.00,
                'paid_amount': 2800.00,
                'payment_status': 'paid',
                'special_requests': '',
            },
        ]
        
        for booking in booking_data:
            # Check if booking already exists
            existing = Booking.objects.filter(
                client=booking['client'],
                package=booking['package'],
                travel_date_start=booking['travel_date_start']
            ).first()
            
            if not existing:
                new_booking = Booking.objects.create(
                    client=booking['client'],
                    package=booking['package'],
                    agent=Agent.objects.first() if Agent.objects.exists() else None,
                    status=booking['status'],
                    travel_date_start=booking['travel_date_start'],
                    travel_date_end=booking['travel_date_end'],
                    total_amount=booking['total_amount'],
                    paid_amount=booking['paid_amount'],
                    payment_status=booking['payment_status'],
                    special_requests=booking['special_requests'],
                    flight_details={
                        'airline': 'Saudia',
                        'flight_number': f'SV{random.randint(100, 999)}',
                        'departure': 'LHR',
                        'arrival': 'JED',
                    },
                    hotel_details={
                        'hotel': 'Makkah Clock Tower',
                        'room_type': 'Deluxe Suite',
                        'nights': 10,
                    },
                )
                self.stdout.write(f'✅ Created booking: {new_booking.booking_id}')
            else:
                self.stdout.write(f'⏩ Booking already exists: {existing.booking_id}')