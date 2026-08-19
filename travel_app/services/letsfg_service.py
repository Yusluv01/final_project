import os
import json
import logging
import requests
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.getLogger(__name__)

class LetsFGService:
    """LetsFG flight search service using API Key"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'LETSFG_API_KEY', None)
        self.available = bool(self.api_key)
        if not self.available:
            logger.warning("LetsFG API Key not found. Falling back to mock data.")
    
    def search_flights(self, origin, destination, date, return_date=None, adults=1):
        """
        Search for flights using LetsFG API Key
        """
        try:
            # Try API search with key
            result = self._search_api(origin, destination, date)
            if result:
                return self._format_results(result, origin, destination)
        except Exception as e:
            logger.error(f"LetsFG API search failed: {e}")
        
        # Fallback to mock data
        return self._get_mock_flights(origin, destination, date)
    
    def _search_api(self, origin, destination, date):
        """Search using LetsFG API with key"""
        try:
            if not self.api_key:
                logger.warning("No API key provided")
                return None
            
            # Note: Since the LetsFG Python package is outdated, we will use their standard API endpoint
            url = "https://api.letsfg.com/v1/search"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "origin": origin,
                "destination": destination,
                "date": date,
                "adults": 1,
                "cabin": "economy"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def _format_results(self, data, origin, destination):
        """Format LetsFG results into standard structure"""
        flights = []
        
        if not data:
            return []
        
        # Handle different response formats
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and 'data' in data:
            items = data.get('data', [])
        elif isinstance(data, dict):
            items = [data]
        else:
            return []
        
        for i, flight in enumerate(items[:20]):
            # Extract basic info
            airline = flight.get('airline', flight.get('carrier', flight.get('airline_name', 'Unknown')))
            price = float(flight.get('price', flight.get('total_price', flight.get('fare', 0))))
            
            # Extract time info
            dep_time = flight.get('departure_time', flight.get('departure', flight.get('departure_at', '')))
            arr_time = flight.get('arrival_time', flight.get('arrival', flight.get('arrival_at', '')))
            
            # Calculate stops
            stops = flight.get('stops', 0)
            if 'segments' in flight:
                stops = len(flight.get('segments', [])) - 1
            
            # Calculate duration
            duration = flight.get('duration', '')
            if not duration and dep_time and arr_time:
                duration = self._calculate_duration(dep_time, arr_time)
            
            flights.append({
                'id': flight.get('id', f"FL{i+1:03d}"),
                'airline': airline,
                'price': price,
                'currency': flight.get('currency', 'USD'),
                'departure': dep_time,
                'arrival': arr_time,
                'duration': duration,
                'stops': stops,
                'origin': origin,
                'destination': destination,
                'booking_url': flight.get('booking_url', flight.get('deep_link', '')),
                'class': flight.get('cabin', 'economy'),
                'raw_data': flight,
            })
        
        return flights
    
    def _calculate_duration(self, dep_time, arr_time):
        """Calculate flight duration from departure and arrival times"""
        try:
            from datetime import datetime
            
            # Try parsing ISO format
            dep = datetime.fromisoformat(dep_time.replace('Z', '+00:00'))
            arr = datetime.fromisoformat(arr_time.replace('Z', '+00:00'))
            
            diff = arr - dep
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            
            if diff.days > 0:
                hours += diff.days * 24
            
            return f"{hours}h {minutes}m"
        except:
            return "Unknown"
    
    def _get_mock_flights(self, origin='LHR', destination='JED', date=None):
        """Generate realistic mock flight data (Fallback)"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        mock_flights = [
            {
                'id': 'FL001',
                'airline': 'Saudia',
                'price': 642.00,
                'currency': 'USD',
                'departure': f"{date}T10:45:00",
                'arrival': f"{date}T18:55:00",
                'duration': '6h 10m',
                'stops': 0,
                'origin': origin,
                'destination': destination,
                'badge': 'HAJJ READY',
                'protocols': ['Meet & Greet', 'Ihram Changing Area'],
                'description': 'Best balance of price, convenience, and Umrah protocol assistance.',
                'booking_url': 'https://www.saudia.com/',
            },
            # ... you can add more here if needed
        ]
        return mock_flights