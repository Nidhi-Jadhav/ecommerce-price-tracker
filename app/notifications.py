from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .config import ALERT_FROM_EMAIL, ALERT_TO_EMAIL, SENDGRID_API_KEY
def send_alert(product):
    recipient = product.alert_email or ALERT_TO_EMAIL
    if not all([SENDGRID_API_KEY, ALERT_FROM_EMAIL, recipient]): return False
    message = Mail(from_email=ALERT_FROM_EMAIL, to_emails=recipient,
      subject=f"Price drop: {product.name}",
      html_content=f"<h2>Target reached</h2><p><b>{product.name}</b> is now ₹{product.current_price:,.2f}, below your target of ₹{product.target_price:,.2f}.</p><p><a href='{product.url}'>View product</a></p>")
    SendGridAPIClient(SENDGRID_API_KEY).send(message)
    return True
