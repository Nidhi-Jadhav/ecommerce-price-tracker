import pytest
from app.scraper import parse_price, retailer_for
def test_price_parser():
    assert parse_price("₹1,299.50") == 1299.50
    assert parse_price(None) is None
def test_retailer_detection():
    assert retailer_for("https://www.amazon.in/dp/example") == "Amazon"
    assert retailer_for("https://www.flipkart.com/example/p/itm") == "Flipkart"
    with pytest.raises(ValueError): retailer_for("https://example.com/item")
