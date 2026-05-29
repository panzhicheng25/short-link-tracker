import os

DOMAIN = os.environ.get("DOMAIN", "nibdl.com")
BASE_URL = f"https://{DOMAIN}"
SECRET_KEY = os.environ.get("SECRET_KEY", "short-link-tracker-secret-2026")
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "root")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "nibbletv666888")
GEOIP_API = "http://ip-api.com/json/{}"
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
PORT = int(os.environ.get("PORT", 5001))
