import pytest
from ProductCatalog import ProductCatalog
from PriceCalculator import PriceCalculator

@pytest.fixture
def price_calculator():
    return PriceCalculator()

@pytest.fixture
def product_catalog(price_calculator):
    return ProductCatalog(price_calculator)

def test_get_product_price_with_tax():
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    laptop_price = catalog.get_product_price("laptop", apply_discount=False)
    expected_price = 1100  # Base price 1000 + 10% tax
    assert laptop_price == expected_price

def test_get_product_price_with_tax_and_discount():
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    laptop_price = catalog.get_product_price("laptop", apply_discount=True)
    expected_price = 1050  # Base price 1000 + 10% tax - 5% discount
    assert laptop_price == expected_price

def test_get_nonexistent_product_price():
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    price = catalog.get_product_price("nonexistent_product")
    assert price is None

def test_multiple_products_calculation():
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    laptop_price = catalog.get_product_price("laptop", apply_discount=True)
    book_price = catalog.get_product_price("book", apply_discount=True)
    
    assert laptop_price == 1050  # Base price 1000 + 10% tax - 5% discount
    assert book_price == 21  # Base price 20 + 10% tax - 5% discount

def test_price_rounding():
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    # Add a temporary product with a price that would result in many decimal places
    catalog.products["test_item"] = {"base_price": 99.99, "category": "test"}
    
    price = catalog.get_product_price("test_item", apply_discount=True)
    assert isinstance(price, float)
    assert str(price)[::-1].find('.') <= 2  # Ensures no more than 2 decimal places