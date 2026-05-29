import requests
from config import GEOIP_API

def get_geo(ip):
    try:
        if ip in ('127.0.0.1', 'localhost', '::1', ''):
            ip = ''
        url = GEOIP_API.format(ip)
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get('status') == 'success':
            return {
                'country': data.get('country', ''),
                'region': data.get('regionName', ''),
                'city': data.get('city', ''),
            }
    except Exception:
        pass
    return {'country': '', 'region': '', 'city': ''}
