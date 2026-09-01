from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .config import ALERT_FROM_EMAIL, ALERT_TO_EMAIL, SENDGRID_API_KEY
def _send(product, subject, heading, description):
    recipient = product.alert_email or ALERT_TO_EMAIL
    if not all([SENDGRID_API_KEY, ALERT_FROM_EMAIL, recipient]): return False
    message = Mail(from_email=ALERT_FROM_EMAIL, to_emails=recipient,
      subject=subject,
      html_content=f"<h2>{heading}</h2><p>{description}</p><p><b>{product.name}</b></p><p><a href='{product.url}'>View product</a></p>")
    SendGridAPIClient(SENDGRID_API_KEY).send(message)
    return True

def send_alert(product):
    return _send(product, f"Price drop: {product.name}", "Target reached", f"This product is now ₹{product.current_price:,.2f}, below your target of ₹{product.target_price:,.2f}.")

def send_test_alert(product):
    return _send(product, f"Test alert: {product.name}", "Email alerts are working", f"This is a test notification for your target price of ₹{product.target_price:,.2f}. You will receive a price-drop alert here when the target is reached.")
