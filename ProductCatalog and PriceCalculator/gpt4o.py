import pytest
from ProductCatalog import ProductCatalog
from PriceCalculator import PriceCalculator

@pytest.fixture
def price_calculator():
    return PriceCalculator()

@pytest.fixture
def product_catalog(price_calculator):
    return ProductCatalog(price_calculator)

def test_get_product_price_with_tax(product_catalog):
    laptop_price = product_catalog.get_product_price("laptop", apply_discount=False)
    expected_price = 1100  # Base price 1000 + 10% tax
    assert laptop_price == expected_price

def test_get_product_price_with_tax_and_discount(product_catalog):
    laptop_price = product_catalog.get_product_price("laptop", apply_discount=True)
    expected_price = 1050  # Base price 1000 + 10% tax - 5% discount
    assert laptop_price == expected_price

def test_get_nonexistent_product_price(product_catalog):
    price = product_catalog.get_product_price("nonexistent_product")
    assert price is None

def test_multiple_products_calculation(product_catalog):
    laptop_price = product_catalog.get_product_price("laptop", apply_discount=False)
    book_price = product_catalog.get_product_price("book", apply_discount=False)
    
    assert laptop_price == 1100  # Base price 1000 + 10% tax
    assert book_price == 22  # Base price 20 + 10% tax

def test_price_calculation_with_discount(product_catalog):
    book_no_discount = product_catalog.get_product_price("book", apply_discount=False)
    book_with_discount = product_catalog.get_product_price("book", apply_discount=True)
    
    expected_discount = 20 * 0.05  # 5% of base price (20)
    assert book_no_discount - book_with_discount == expected_discount

def test_custom_tax_rate(price_calculator):
    price_calculator.tax_rate = 0.2  # Change tax rate to 20%
    catalog = ProductCatalog(price_calculator)
    
    laptop_price = catalog.get_product_price("laptop", apply_discount=False)
    expected_price = 1200  # Base price 1000 + 20% tax
    assert laptop_price == expected_price

def test_custom_discount_rate(price_calculator):
    price_calculator.discount_rate = 0.1  # Change discount rate to 10%
    catalog = ProductCatalog(price_calculator)
    
    laptop_price = catalog.get_product_price("laptop", apply_discount=True)
    expected_price = 1000  # Base price 1000 + 10% tax - 10% discount
    assert laptop_price == expected_price

def test_rounding_behavior(product_catalog):
    # Add a temporary product with a price that would result in decimal places
    product_catalog.products["test_item"] = {"base_price": 9.99, "category": "test"}
    
    price = product_catalog.get_product_price("test_item", apply_discount=True)
    expected_price = 10.49  # 9.99 + 10% tax - 5% discount = 10.489, rounded to 10.49
    assert price == expected_price