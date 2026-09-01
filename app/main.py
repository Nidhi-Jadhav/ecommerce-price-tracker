from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Product
from .scraper import retailer_for
from .services import check_product
@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine); yield
app = FastAPI(title="E-commerce Price Tracker", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
@app.get("/health")
def health(): return {"status": "ok"}
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "index.html", {"products": db.query(Product).order_by(Product.created_at.desc()).all()})
@app.post("/products")
def add_product(url: str = Form(...), target_price: float = Form(...), db: Session = Depends(get_db)):
    try: retailer = retailer_for(url)
    except ValueError as error: raise HTTPException(400, str(error))
    if db.query(Product).filter(Product.url == url).first(): raise HTTPException(409, "This URL is already tracked.")
    product = Product(name="Fetching product details…", url=url, retailer=retailer, target_price=target_price)
    db.add(product); db.commit(); db.refresh(product)
    try: check_product(db, product)
    except Exception: pass
    return RedirectResponse("/", status_code=303)
@app.post("/products/{product_id}/check")
def check(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product: raise HTTPException(404, "Product not found")
    try: check_product(db, product)
    except Exception as error: raise HTTPException(502, str(error))
    return RedirectResponse("/", status_code=303)
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
