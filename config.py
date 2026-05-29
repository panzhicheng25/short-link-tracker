import os

DOMAIN = os.environ.get("DOMAIN", "nibdl.com")
BASE_URL = f"http://{DOMAIN}"
SECRET_KEY = os.environ.get("SECRET_KEY", "short-link-tracker-secret-2026")
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123456")
GEOIP_API = "http://ip-api.com/json/{}"
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
PORT = int(os.environ.get("PORT", 5001))
