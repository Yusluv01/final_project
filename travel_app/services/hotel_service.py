import requests
from django.conf import settings

def get_amadeus_token():
    """Get an access token from Amadeus"""
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.AMADEUS_API_KEY,
        "client_secret": settings.AMADEUS_API_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get('access_token')

def search_hotels(city_code, check_in_date, check_out_date, adults=2):
    """Search for real hotels using Amadeus API"""
    try:
        token = get_amadeus_token()
        url = "https://test.api.amadeus.com/v2/shopping/hotel-offers"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "cityCode": city_code,          # 'JED' for Makkah, 'MED' for Madinah
            "checkInDate": check_in_date,   # '2026-08-01'
            "checkOutDate": check_out_date, # '2026-08-05'
            "adults": adults,
            "roomQuantity": 1,
            "currency": "USD",
            "max": 10
        }
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except Exception as e:
        print(f"Amadeus Hotel API Error: {e}")
        return []