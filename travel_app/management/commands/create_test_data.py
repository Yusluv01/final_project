from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from travel_app.models import Agent, Client, TravelPackage, Booking

class Command(BaseCommand):
    help = 'Create test data for development'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Create admin user
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
            self.stdout.write(self.style.SUCCESS('Admin user created'))
        
        # Create test packages
        packages = [
            {'name': 'Hajj 2024 Premium', 'package_type': 'hajj_2024', 'price': 4500.00, 'duration_days': 14},
            {'name': 'Umrah 2024 Standard', 'package_type': 'umrah', 'price': 2500.00, 'duration_days': 10},
        ]
        
        for pkg_data in packages:
            pkg, created = TravelPackage.objects.get_or_create(
                name=pkg_data['name'],
                defaults={
                    'package_type': pkg_data['package_type'],
                    'price': pkg_data['price'],
                    'duration_days': pkg_data['duration_days'],
                    'description': f'Comprehensive {pkg_data["name"]} package.',
                    'available_from': timezone.now().date(),
                    'available_until': timezone.now().date() + timedelta(days=365),
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'Created package: {pkg.name}')
        
        self.stdout.write(self.style.SUCCESS('Test data creation complete!'))