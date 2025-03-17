import pytest
from unittest.mock import Mock, patch, call
import logging
from ProductCatalog import ProductCatalog
from PriceCalculator import PriceCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestProductPriceIntegration:
    @pytest.fixture
    def mock_calculator(self):
        return Mock(spec=PriceCalculator)
    
    @pytest.fixture
    def real_calculator(self):
        return PriceCalculator()
    
    @pytest.fixture
    def catalog(self, real_calculator):
        return ProductCatalog(real_calculator)

    # Success Path Tests
    def test_successful_price_calculation(self, catalog):
        result = catalog.get_product_price("laptop", apply_discount=False)
        assert result == 1100  # 1000 + 10% tax
        
        result_with_discount = catalog.get_product_price("laptop", apply_discount=True)
        assert result_with_discount == 1050  # 1000 + 10% tax - 5% discount

    def test_data_flow_accuracy(self, mock_calculator):
        catalog = ProductCatalog(mock_calculator)
        catalog.get_product_price("laptop", apply_discount=True)
        
        mock_calculator.calculate_final_price.assert_called_once_with(
            1000, apply_tax=True, apply_discount=True
        )

    # Failure Path Tests
    def test_calculator_failure(self, mock_calculator):
        mock_calculator.calculate_final_price.side_effect = ValueError("Calculation failed")
        catalog = ProductCatalog(mock_calculator)
        
        with pytest.raises(ValueError) as exc_info:
            catalog.get_product_price("laptop")
        assert str(exc_info.value) == "Calculation failed"

    def test_nonexistent_product(self, catalog):
        result = catalog.get_product_price("nonexistent")
        assert result is None

    # Edge Cases
    def test_zero_price_product(self, catalog):
        catalog.products["free_item"] = {"base_price": 0, "category": "promotion"}
        result = catalog.get_product_price("free_item")
        assert result == 0

    def test_negative_price(self, catalog):
        catalog.products["refund"] = {"base_price": -100, "category": "refund"}
        result = catalog.get_product_price("refund")
        assert result == -110  # -100 + 10% tax

    def test_large_numbers(self, catalog):
        catalog.products["expensive"] = {"base_price": 999999.99, "category": "luxury"}
        result = catalog.get_product_price("expensive", apply_discount=True)
        expected = round(999999.99 + (999999.99 * 0.1) - (999999.99 * 0.05), 2)
        assert result == expected

    def test_floating_point_precision(self, catalog):
        catalog.products["precise"] = {"base_price": 9.99, "category": "test"}
        result = catalog.get_product_price("precise", apply_discount=True)
        expected = round(9.99 + (9.99 * 0.1) - (9.99 * 0.05), 2)
        assert result == expected

    # State Management Tests
    def test_calculator_state_changes(self, catalog):
        original_price = catalog.get_product_price("laptop")
        catalog.price_calculator.tax_rate = 0.2
        
        new_price = catalog.get_product_price("laptop")
        assert new_price > original_price
        assert new_price == round(1000 * 1.2, 2)

    def test_multiple_products_sequence(self, mock_calculator):
        catalog = ProductCatalog(mock_calculator)
        mock_calculator.calculate_final_price.side_effect = [1100, 22]
        
        laptop_price = catalog.get_product_price("laptop")
        book_price = catalog.get_product_price("book")
        
        assert mock_calculator.calculate_final_price.call_count == 2
        assert laptop_price == 1100
        assert book_price == 22