import random
from datetime import datetime, timedelta

class MockFlightService:
    def __init__(self):
        self.airlines = [
            {'name': 'Saudia', 'code': 'SV', 'logo': 'saudia.png'},
            {'name': 'Emirates', 'code': 'EK', 'logo': 'emirates.png'},
            {'name': 'Qatar Airways', 'code': 'QR', 'logo': 'qatar.png'},
            {'name': 'Etihad Airways', 'code': 'EY', 'logo': 'etihad.png'},
            {'name': 'Turkish Airlines', 'code': 'TK', 'logo': 'turkish.png'},
            {'name': 'British Airways', 'code': 'BA', 'logo': 'british.png'},
            {'name': 'Lufthansa', 'code': 'LH', 'logo': 'lufthansa.png'},
            {'name': 'Air France', 'code': 'AF', 'logo': 'airfrance.png'},
        ]
        
        self.routes = {
            'LHR-JED': {'duration': '6h 15m', 'price_range': (350, 750), 'cities': ('London', 'Jeddah'), 'badge': 'HAJJ ROUTE'},
            'LHR-MED': {'duration': '5h 45m', 'price_range': (380, 780), 'cities': ('London', 'Medina'), 'badge': 'HAJJ ROUTE'},
            'JFK-DXB': {'duration': '12h 30m', 'price_range': (800, 1400), 'cities': ('New York', 'Dubai'), 'badge': 'PREMIUM'},
            'LHR-KHI': {'duration': '7h 45m', 'price_range': (400, 750), 'cities': ('London', 'Karachi'), 'badge': 'POPULAR'},
            'MAN-JED': {'duration': '6h 30m', 'price_range': (370, 720), 'cities': ('Manchester', 'Jeddah'), 'badge': 'HAJJ ROUTE'},
            'JED-DXB': {'duration': '2h 30m', 'price_range': (200, 450), 'cities': ('Jeddah', 'Dubai'), 'badge': 'REGIONAL'},
            'JED-MED': {'duration': '1h 15m', 'price_range': (100, 250), 'cities': ('Jeddah', 'Medina'), 'badge': 'DOMESTIC'},
            'LHR-DXB': {'duration': '7h 00m', 'price_range': (500, 900), 'cities': ('London', 'Dubai'), 'badge': 'PREMIUM'},
            'JFK-JED': {'duration': '11h 30m', 'price_range': (750, 1300), 'cities': ('New York', 'Jeddah'), 'badge': 'HAJJ ROUTE'},
            'JFK-MED': {'duration': '11h 00m', 'price_range': (780, 1350), 'cities': ('New York', 'Medina'), 'badge': 'HAJJ ROUTE'},
            'DXB-MED': {'duration': '2h 45m', 'price_range': (250, 500), 'cities': ('Dubai', 'Medina'), 'badge': 'REGIONAL'},
            'LHR-ISB': {'duration': '7h 30m', 'price_range': (420, 700), 'cities': ('London', 'Islamabad'), 'badge': 'POPULAR'},
        }
    
    def search_flights(self, origin, destination, date):
        """Return mock flight results for the given route"""
        route_key = f"{origin}-{destination}"
        
        if route_key not in self.routes:
            route_key = f"{destination}-{origin}"
            if route_key not in self.routes:
                return []
        
        route_data = self.routes[route_key]
        flights = []
        num_flights = random.randint(5, 8)
        
        for i in range(num_flights):
            airline = random.choice(self.airlines)
            departure_hour = random.randint(6, 22)
            departure_minute = random.randint(0, 59)
            
            duration_parts = route_data['duration'].split('h ')
            dur_hours = int(duration_parts[0])
            dur_minutes = int(duration_parts[1].replace('m', '')) if len(duration_parts) > 1 else 0
            
            arrival_hour = (departure_hour + dur_hours + (departure_minute + dur_minutes) // 60) % 24
            arrival_minute = (departure_minute + dur_minutes) % 60
            
            base_price = random.uniform(route_data['price_range'][0], route_data['price_range'][1])
            if 7 <= departure_hour <= 9 or 16 <= departure_hour <= 18:
                base_price *= 1.15
            price = round(base_price, 2)
            
            if random.random() < 0.3:
                stops = random.randint(1, 2)
                duration_str = f"{dur_hours + (stops * 2):02d}h {(dur_minutes + (stops * 30)) % 60:02d}m"
            else:
                stops = 0
                duration_str = route_data['duration']
            
            flight = {
                'id': f"{airline['code']}{random.randint(100, 999)}",
                'airline': airline['name'],
                'airline_code': airline['code'],
                'flight_number': f"{airline['code']}{random.randint(100, 999)}",
                'price': price,
                'currency': 'USD',
                'departure': f"{departure_hour:02d}:{departure_minute:02d}",
                'arrival': f"{arrival_hour:02d}:{arrival_minute:02d}",
                'duration': duration_str,
                'stops': stops,
                'origin': origin,
                'destination': destination,
                'badge': route_data.get('badge', ''),
                'protocols': ['Standard', 'Checked Baggage Included'] if random.random() < 0.5 else ['Standard'],
                'description': f"Direct flight from {route_data['cities'][0]} to {route_data['cities'][1]}",
                'booking_url': f"https://travelbolt.ai/book/{airline['code']}{random.randint(100, 999)}",
                'available_seats': random.randint(15, 120)
            }
            flights.append(flight)
        
        return sorted(flights, key=lambda x: x['price'])