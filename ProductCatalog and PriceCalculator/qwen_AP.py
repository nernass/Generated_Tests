import pytest
from unittest.mock import MagicMock

class PriceCalculator:
    def __init__(self):
        self.tax_rate = 0.1
        self.discount_rate = 0.05

    def calculate_final_price(self, base_price, apply_tax=True, apply_discount=False):
        price = base_price
        if apply_tax:
            price += base_price * self.tax_rate
        if apply_discount:
            price -= base_price * self.discount_rate
        return round(price, 2)

class ProductCatalog:
    def __init__(self, price_calculator):
        self.products = {
            "laptop": {"base_price": 1000, "category": "electronics"},
            "book": {"base_price": 20, "category": "media"}
        }
        self.price_calculator = price_calculator

    def get_product_price(self, product_id, apply_discount=False):
        if product_id in self.products:
            base_price = self.products[product_id]["base_price"]
            return self.price_calculator.calculate_final_price(base_price, apply_tax=True, apply_discount=apply_discount)
        return None

@pytest.fixture
def price_calculator():
    return PriceCalculator()

@pytest.fixture
def product_catalog(price_calculator):
    return ProductCatalog(price_calculator)

class TestIntegrationPriceCalculatorAndProductCatalog:

    def test_success_path_get_product_price_with_tax(self, product_catalog):
        price = product_catalog.get_product_price("laptop")
        assert price == 1100.0

    def test_success_path_get_product_price_with_tax_and_discount(self, product_catalog):
        price = product_catalog.get_product_price("laptop", apply_discount=True)
        assert price == 1045.0

    def test_success_path_get_product_price_for_book_with_tax(self, product_catalog):
        price = product_catalog.get_product_price("book")
        assert price == 22.0

    def test_success_path_get_product_price_for_book_with_tax_and_discount(self, product_catalog):
        price = product_catalog.get_product_price("book", apply_discount=True)
        assert price == 20.9

    def test_partial_failure_product_id_not_found(self, product_catalog):
        price = product_catalog.get_product_price("nonexistent")
        assert price is None

    def test_partial_failure_price_calculator_throws_exception(self, product_catalog, price_calculator):
        price_calculator.calculate_final_price = MagicMock(side_effect=Exception("Calculation failed"))
        with pytest.raises(Exception) as excinfo:
            product_catalog.get_product_price("laptop")
        assert str(excinfo.value) == "Calculation failed"

    def test_edge_case_zero_base_price(self, product_catalog, price_calculator):
        product_catalog.products["laptop"]["base_price"] = 0
        price = product_catalog.get_product_price("laptop")
        assert price == 0.0

    def test_edge_case_large_base_price(self, product_catalog, price_calculator):
        product_catalog.products["laptop"]["base_price"] = 1000000
        price = product_catalog.get_product_price("laptop")
        assert price == 1100000.0

    def test_edge_case_empty_product_id(self, product_catalog):
        price = product_catalog.get_product_price("")
        assert price is None

    def test_edge_case_special_characters_in_product_id(self, product_catalog):
        price = product_catalog.get_product_price("!@#")
        assert price is None

    def test_edge_case_large_product_id(self, product_catalog):
        long_product_id = "a" * 100
        price = product_catalog.get_product_price(long_product_id)
        assert price is None

    def test_edge_case_negative_base_price(self, product_catalog, price_calculator):
        product_catalog.products["laptop"]["base_price"] = -1000
        price = product_catalog.get_product_price("laptop")
        assert price == -1100.0

    def test_edge_case_float_base_price(self, product_catalog, price_calculator):
        product_catalog.products["laptop"]["base_price"] = 1000.5
        price = product_catalog.get_product_price("laptop")
        assert price == 1100.55

    def test_edge_case_high_discount_rate(self, product_catalog, price_calculator):
        price_calculator.discount_rate = 0.95
        price = product_catalog.get_product_price("laptop", apply_discount=True)
        assert price == 110.0

    def test_edge_case_high_tax_rate(self, product_catalog, price_calculator):
        price_calculator.tax_rate = 0.95
        price = product_catalog.get_product_price("laptop")
        assert price == 1950.0