# location/views.py

import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def get_location(request):
    # Get IP address
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '') or request.META.get('REMOTE_ADDR')
    logger.info(f"Received request from IP: {ip_address}")
    
    # If localhost, use a fallback IP for testing
    if ip_address in ('127.0.0.1', '::1'):
        ip_address = '8.8.8.8'  # Google's public DNS IP
        logger.info(f"Local testing detected. Using fallback IP: {ip_address}")
    
    # Initialize variables
    country = region = city = town = state = latitude = longitude = None
    
    try:
        # Use ipapi.co to get location data
        logger.info(f"Requesting data from ipapi.co for IP: {ip_address}")
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        logger.info(f"ipapi.co response status: {response.status_code}")
        logger.info(f"ipapi.co response content: {response.text}")
        
        response.raise_for_status()
        location_data = response.json()

        # Extract relevant information
        country = location_data.get('country_name')
        region = location_data.get('region')
        city = location_data.get('city')
        latitude = location_data.get('latitude')
        longitude = location_data.get('longitude')

        logger.info(f"Extracted data: country={country}, region={region}, city={city}, lat={latitude}, lon={longitude}")

        # If you need more detailed information, use Nominatim for reverse geocoding
        if latitude and longitude:
            logger.info(f"Requesting data from Nominatim for lat={latitude}, lon={longitude}")
            nominatim_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
            nominatim_response = requests.get(nominatim_url, headers={'User-Agent': 'YourApp/1.0'})
            logger.info(f"Nominatim response status: {nominatim_response.status_code}")
            logger.info(f"Nominatim response content: {nominatim_response.text}")
            
            nominatim_response.raise_for_status()
            nominatim_data = nominatim_response.json()
            
            # Extract more detailed address information if available
            address = nominatim_data.get('address', {})
            town = address.get('town') or address.get('village') or city
            state = address.get('state') or region

            logger.info(f"Extracted additional data: town={town}, state={state}")

    except requests.RequestException as e:
        logger.error(f"Error occurred while fetching location data: {str(e)}")
        return JsonResponse({'error': f"Failed to fetch location data: {str(e)}"}, status=500)

    result = {
        'country': country,
        'state': state,
        'region': region,
        'city': city,
        'town': town,
        'latitude': latitude,
        'longitude': longitude,
    }
    logger.info(f"Returning result: {result}")
    return JsonResponse(result)