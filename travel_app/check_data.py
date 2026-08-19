# check_data.py
from travel_app.models import TravelPackage, Client, Booking

# ==================== PACKAGES ====================
print("=" * 50)
print("TRAVEL PACKAGES")
print("=" * 50)

packages = TravelPackage.objects.all()
print(f"Total packages: {packages.count()}")
for pkg in packages:
    print(f"  - {pkg.name}: ${pkg.price} ({pkg.get_package_type_display()})")

# ==================== CLIENTS ====================
print("\n" + "=" * 50)
print("CLIENTS")
print("=" * 50)

clients = Client.objects.all()
print(f"Total clients: {clients.count()}")
for client in clients:
    print(f"  - {client.first_name} {client.last_name} ({client.travel_type})")

# ==================== BOOKINGS ====================
print("\n" + "=" * 50)
print("BOOKINGS")
print("=" * 50)

bookings = Booking.objects.all()
print(f"Total bookings: {bookings.count()}")
for booking in bookings:
    package_name = booking.package.name if booking.package else "No Package"
    print(f"  - {booking.booking_id}: {booking.client.first_name} - {package_name} ({booking.status})")

# ==================== SUMMARY ====================
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
print(f"📦 Packages: {packages.count()}")
print(f"👤 Clients: {clients.count()}")
print(f"📋 Bookings: {bookings.count()}")
print("=" * 50)