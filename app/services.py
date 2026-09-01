from datetime import datetime
from sqlalchemy.orm import Session
from .models import Product, PriceObservation
from .scraper import scrape
from .notifications import send_alert
def check_product(db: Session, product: Product):
    result = scrape(product.url)
    product.name, product.current_price, product.image_url = result.name, result.price, result.image_url
    product.last_checked_at = datetime.utcnow()
    db.add(PriceObservation(product_id=product.id, price=result.price))
    db.commit(); db.refresh(product)
    if result.price > product.target_price and product.alert_sent_at:
        product.alert_sent_at = None
        db.commit()
    if result.price <= product.target_price and not product.alert_sent_at:
        send_alert(product)
        product.alert_sent_at = datetime.utcnow()
        db.commit()
    return product
def check_all(db: Session):
    outcomes = []
    for product in db.query(Product).all():
        try: check_product(db, product); outcomes.append((product.id, "checked"))
        except Exception as error: outcomes.append((product.id, str(error)))
    return outcomes
