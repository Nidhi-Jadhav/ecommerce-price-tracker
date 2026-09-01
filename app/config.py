import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./price_tracker.db").strip()
# Deployment dashboards can preserve an accidental trailing newline when a
# secret is pasted. Trim it before using the value in an HTTP header.
SENDGRID_API_KEY = (os.getenv("SENDGRID_API_KEY") or "").strip()
ALERT_FROM_EMAIL = (os.getenv("ALERT_FROM_EMAIL") or "").strip()
ALERT_TO_EMAIL = (os.getenv("ALERT_TO_EMAIL") or "").strip()
