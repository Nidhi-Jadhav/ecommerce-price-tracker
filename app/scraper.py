import json, re
from dataclasses import dataclass
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PersonalPriceTracker/1.0)"}
@dataclass
class ScrapedProduct:
    name: str
    price: float
    image_url: str | None = None
def retailer_for(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "amazon." in host: return "Amazon"
    if "flipkart." in host: return "Flipkart"
    raise ValueError("Only Amazon and Flipkart product URLs are supported.")
def parse_price(value):
    cleaned = re.sub(r"[^0-9.]", "", str(value or "").replace(",", ""))
    try: return float(cleaned) if cleaned else None
    except ValueError: return None
def _json_ld(soup):
    for node in soup.select('script[type="application/ld+json"]'):
        try:
            items = json.loads(node.string or "{}")
            for item in items if isinstance(items, list) else [items]:
                if item.get("@type") == "Product":
                    offers = item.get("offers", {})
                    if isinstance(offers, list): offers = offers[0]
                    image = item.get("image")
                    return item.get("name"), parse_price(offers.get("price")), image if isinstance(image, str) else None
        except (json.JSONDecodeError, AttributeError): pass
    return None, None, None
def scrape(url: str) -> ScrapedProduct:
    retailer = retailer_for(url)
    response = requests.get(url, headers=HEADERS, timeout=20); response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title, price, image = _json_ld(soup)
    if retailer == "Amazon":
        title = title or (soup.select_one("#productTitle") or {}).get_text(strip=True)
        price = price or parse_price((soup.select_one(".a-price .a-offscreen") or {}).get_text(strip=True))
        image = image or (soup.select_one("#landingImage") or {}).get("src")
    else:
        title = title or (soup.select_one("span.VU-ZEz") or {}).get_text(strip=True)
        price = price or parse_price((soup.select_one("div.Nx9bqj") or {}).get_text(strip=True))
        image = image or (soup.select_one("img._53J4C-") or {}).get("src")
    if not title or price is None: raise ValueError("Could not read a product price; the retailer may have changed its page or blocked this request.")
    return ScrapedProduct(title, price, image)
