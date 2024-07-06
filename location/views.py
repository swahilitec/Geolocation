# location/views.py

from django.http import JsonResponse
import requests

def get_location(request):
    ip = request.GET.get('ip', request.META.get('REMOTE_ADDR'))
    if ip == '127.0.0.1':  # Local testing override
        ip = '8.8.8.9'  # Example public IP address for testing purposes
    response = requests.get(f"https://ipinfo.io/{ip}/json")
    data = response.json()
    return JsonResponse(data)
