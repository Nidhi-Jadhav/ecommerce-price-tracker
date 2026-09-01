from contextlib import asynccontextmanager
from urllib.parse import urlencode
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import ensure_schema, get_db
from .models import Product
from .scraper import retailer_for
from .services import check_product
from .notifications import send_test_alert
import logging

logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app):
    ensure_schema(); yield
app = FastAPI(title="E-commerce Price Tracker", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
@app.get("/health")
def health(): return {"status": "ok"}
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "index.html", {"products": db.query(Product).order_by(Product.created_at.desc()).all(), "notice": request.query_params.get("notice"), "error": request.query_params.get("error")})
@app.post("/products")
def add_product(url: str = Form(...), target_price: float = Form(...), alert_email: str = Form(...), db: Session = Depends(get_db)):
    alert_email = alert_email.strip().lower()
    if "@" not in alert_email or alert_email.startswith("@") or alert_email.endswith("@"):
        return RedirectResponse("/?" + urlencode({"error": "Enter a valid email address for price alerts."}), status_code=303)
    try: retailer = retailer_for(url)
    except ValueError as error:
        return RedirectResponse("/?" + urlencode({"error": str(error)}), status_code=303)
    if db.query(Product).filter(Product.url == url).first():
        return RedirectResponse("/?" + urlencode({"error": "This product is already in your watchlist."}), status_code=303)
    product = Product(name="Fetching product details…", url=url, retailer=retailer, target_price=target_price, alert_email=alert_email)
    db.add(product); db.commit(); db.refresh(product)
    try:
        check_product(db, product)
    except Exception:
        logger.exception("Initial price check or alert failed for product %s", product.id)
        return RedirectResponse("/?" + urlencode({"notice": "Product added to your watchlist.", "error": "The first price check or email alert failed. Use Check now to retry."}), status_code=303)
    return RedirectResponse("/?" + urlencode({"notice": "Product added to your watchlist."}), status_code=303)
@app.post("/products/{product_id}/check")
def check(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product: raise HTTPException(404, "Product not found")
    try: check_product(db, product)
    except Exception:
        logger.exception("Price check or alert failed for product %s", product.id)
        return RedirectResponse("/?" + urlencode({"error": "The price check or email alert failed. Check the Render logs, then try again."}), status_code=303)
    return RedirectResponse("/", status_code=303)
@app.post("/products/{product_id}/test-alert")
def test_alert(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product: raise HTTPException(404, "Product not found")
    try:
        if not send_test_alert(product):
            return RedirectResponse("/?" + urlencode({"error": "Email is not configured for this product."}), status_code=303)
    except Exception:
        return RedirectResponse("/?" + urlencode({"error": "The test email could not be sent. Check your SendGrid sender and API key."}), status_code=303)
    return RedirectResponse("/?" + urlencode({"notice": f"Test email sent to {product.alert_email or 'the configured recipient'}."}), status_code=303)
@app.post("/products/{product_id}/delete")
def delete(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product: raise HTTPException(404, "Product not found")
    db.delete(product); db.commit(); return RedirectResponse("/", status_code=303)
@app.get("/api/products")
def products(db: Session = Depends(get_db)):
    return [{"id": p.id, "name": p.name, "retailer": p.retailer, "price": p.current_price, "target": p.target_price, "url": p.url} for p in db.query(Product).all()]
@app.get("/api/products/{product_id}/history")
def history(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product: raise HTTPException(404, "Product not found")
    return [{"price": x.price, "observed_at": x.observed_at.isoformat()} for x in product.observations]
