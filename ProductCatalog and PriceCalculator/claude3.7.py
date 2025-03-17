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
    # Test basic price calculation with tax
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    laptop_price = catalog.get_product_price("laptop", apply_discount=False)
    expected_price = 1100  # Base price 1000 + 10% tax
    assert laptop_price == expected_price

def test_get_product_price_with_tax_and_discount():
    # Test price calculation with both tax and discount
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    laptop_price = catalog.get_product_price("laptop", apply_discount=True)
    expected_price = 950  # Base price 1000 + 10% tax - 5% discount
    assert laptop_price == expected_price

def test_get_nonexistent_product_price():
    # Test handling of nonexistent products
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    price = catalog.get_product_price("nonexistent_product")
    assert price is None

def test_multiple_products_calculation():
    # Test consistent calculation across multiple products
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    laptop_price = catalog.get_product_price("laptop", apply_discount=False)
    book_price = catalog.get_product_price("book", apply_discount=False)
    
    assert laptop_price == 1100  # Base price 1000 + 10% tax
    assert book_price == 22  # Base price 20 + 10% tax

def test_price_calculation_with_discount():
    # Test discount application is consistent
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    book_no_discount = catalog.get_product_price("book", apply_discount=False)
    book_with_discount = catalog.get_product_price("book", apply_discount=True)
    
    expected_discount = calculator.discount_rate * 20  # 5% of base price (20)
    assert book_no_discount - book_with_discount == expected_discount

def test_custom_tax_rate():
    # Test with modified tax rate
    calculator = PriceCalculator()
    calculator.tax_rate = 0.2  # Change tax rate to 20%
    catalog = ProductCatalog(calculator)
    
    laptop_price = catalog.get_product_price("laptop", apply_discount=False)
    expected_price = 1200  # Base price 1000 + 20% tax
    assert laptop_price == expected_price

def test_custom_discount_rate():
    # Test with modified discount rate
    calculator = PriceCalculator()
    calculator.discount_rate = 0.1  # Change discount rate to 10%
    catalog = ProductCatalog(calculator)
    
    laptop_price = catalog.get_product_price("laptop", apply_discount=True)
    expected_price = 1000  # Base price 1000 + 10% tax - 10% discount
    assert laptop_price == expected_price

def test_rounding_behavior():
    # Test rounding behavior with prices that would result in many decimal places
    calculator = PriceCalculator()
    catalog = ProductCatalog(calculator)
    
    # Add a temporary product with a price that would result in decimal places
    catalog.products["test_item"] = {"base_price": 9.99, "category": "test"}
    
    price = catalog.get_product_price("test_item", apply_discount=True)
    expected_price = 10.49  # 9.99 + 10% tax - 5% discount = 10.489, rounded to 10.49
    assert price == expected_price