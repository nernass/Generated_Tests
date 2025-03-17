import pytest
from unittest.mock import MagicMock
from PriceCalculator import PriceCalculator
from ProductCatalog import ProductCatalog

class TestIntegrationProductCatalog:
    def setup_method(self):
        self.mock_calculator = MagicMock(spec=PriceCalculator)
        self.catalog = ProductCatalog(self.mock_calculator)

    def test_valid_product_with_discount(self):
        self.mock_calculator.calculate_final_price.return_value = 950.0
        price = self.catalog.get_product_price("laptop", apply_discount=True)
        
        assert price == 950.0
        self.mock_calculator.calculate_final_price.assert_called_once_with(1000, True, True)

    def test_valid_product_without_discount(self):
        self.mock_calculator.calculate_final_price.return_value = 1100.0
        price = self.catalog.get_product_price("laptop")
        
        assert price == 1100.0
        self.mock_calculator.calculate_final_price.assert_called_once_with(1000, True, False)

    def test_invalid_product_handling(self):
        price = self.catalog.get_product_price("invalid_product")
        assert price is None
        self.mock_calculator.calculate_final_price.assert_not_called()

    def test_calculator_exception_propagation(self):
        self.mock_calculator.calculate_final_price.side_effect = ValueError("Invalid price")
        with pytest.raises(ValueError) as exc_info:
            self.catalog.get_product_price("laptop")
        assert "Invalid price" in str(exc_info.value)

    def test_edge_case_zero_base_price(self):
        self.catalog.products["free_item"] = {"base_price": 0.0, "category": "test"}
        self.mock_calculator.calculate_final_price.return_value = 0.0
        
        assert self.catalog.get_product_price("free_item") == 0.0
        self.mock_calculator.calculate_final_price.assert_called_once_with(0.0, True, False)

    def test_real_integration_flow(self):
        real_calculator = PriceCalculator()
        catalog = ProductCatalog(real_calculator)
        
        assert catalog.get_product_price("laptop", True) == 1050.0  # 1000 + 100 (tax) - 50 (discount)
        assert catalog.get_product_price("book", True) == 21.0  # 20 + 2 (tax) - 1 (discount)
        assert catalog.get_product_price("book") == 22.0  # 20 + 2 (tax)