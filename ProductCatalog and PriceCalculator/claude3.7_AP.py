import pytest
from unittest.mock import Mock, patch, call
from ProductCatalog import ProductCatalog
from PriceCalculator import PriceCalculator

class TestProductCatalogPriceCalculatorIntegration:
    
    @pytest.fixture
    def price_calculator(self):
        return PriceCalculator()
    
    @pytest.fixture
    def product_catalog(self, price_calculator):
        return ProductCatalog(price_calculator)
    
    @pytest.fixture
    def mock_price_calculator(self):
        return Mock(spec=PriceCalculator)
    
    # SUCCESS PATH TESTS
    
    def test_success_path_laptop_no_discount(self, product_catalog, price_calculator):
        # Mock to track the call
        with patch.object(price_calculator, 'calculate_final_price', wraps=price_calculator.calculate_final_price) as mock_calc:
            result = product_catalog.get_product_price("laptop", apply_discount=False)
            
            # Verify the data flow
            mock_calc.assert_called_once_with(1000, apply_tax=True, apply_discount=False)
            assert result == 1100  # Base price 1000 + 10% tax
    
    def test_success_path_book_with_discount(self, product_catalog, price_calculator):
        with patch.object(price_calculator, 'calculate_final_price', wraps=price_calculator.calculate_final_price) as mock_calc:
            result = product_catalog.get_product_price("book", apply_discount=True)
            
            # Verify the data flow
            mock_calc.assert_called_once_with(20, apply_tax=True, apply_discount=True)
            assert result == 21  # Base price 20 + 10% tax - 5% discount = 21
    
    def test_end_to_end_workflow(self, price_calculator):
        # Test complete workflow with modified rates
        price_calculator.tax_rate = 0.15
        price_calculator.discount_rate = 0.1
        
        catalog = ProductCatalog(price_calculator)
        
        # Test multiple products in sequence
        laptop_price = catalog.get_product_price("laptop", apply_discount=True)
        book_price = catalog.get_product_price("book", apply_discount=False)
        
        # Expected: laptop (1000 + 15% - 10% = 1050), book (20 + 15% = 23)
        assert laptop_price == 1050
        assert book_price == 23
    
    # FAILURE PATH TESTS
    
    def test_calculator_exception_propagation(self, mock_price_calculator):
        mock_price_calculator.calculate_final_price.side_effect = ValueError("Invalid price calculation")
        catalog = ProductCatalog(mock_price_calculator)
        
        with pytest.raises(ValueError, match="Invalid price calculation"):
            catalog.get_product_price("laptop", apply_discount=False)
        
        # Verify the interaction happened before the exception
        mock_price_calculator.calculate_final_price.assert_called_once_with(1000, apply_tax=True, apply_discount=False)
    
    def test_nonexistent_product_handling(self, product_catalog, price_calculator):
        with patch.object(price_calculator, 'calculate_final_price') as mock_calc:
            result = product_catalog.get_product_price("nonexistent", apply_discount=False)
            
            # Verify calculator is not called for nonexistent products
            mock_calc.assert_not_called()
            assert result is None
    
    # EDGE CASE TESTS
    
    def test_zero_price_product(self, product_catalog, price_calculator):
        # Add a zero-price product
        product_catalog.products["free_sample"] = {"base_price": 0, "category": "promotion"}
        
        with patch.object(price_calculator, 'calculate_final_price', wraps=price_calculator.calculate_final_price) as mock_calc:
            result = product_catalog.get_product_price("free_sample", apply_discount=True)
            
            # Verify calculator receives the zero price
            mock_calc.assert_called_once_with(0, apply_tax=True, apply_discount=True)
            assert result == 0
    
    def test_negative_price_product(self, product_catalog, price_calculator):
        # Add a product with negative price (e.g., a refund)
        product_catalog.products["refund_item"] = {"base_price": -50, "category": "refund"}
        
        with patch.object(price_calculator, 'calculate_final_price', wraps=price_calculator.calculate_final_price) as mock_calc:
            result = product_catalog.get_product_price("refund_item", apply_discount=False)
            
            # Verify calculator handles negative price correctly
            mock_calc.assert_called_once_with(-50, apply_tax=True, apply_discount=False)
            assert result == -55  # -50 + 10% tax = -55
    
    def test_extremely_large_price(self, product_catalog, price_calculator):
        # Test with a very large number to check for overflow issues
        product_catalog.products["expensive_item"] = {"base_price": 10000000, "category": "luxury"}
        
        result = product_catalog.get_product_price("expensive_item", apply_discount=True)
        expected = 10000000 + (10000000 * 0.1) - (10000000 * 0.05)
        assert result == expected
    
    def test_floating_point_rounding(self, product_catalog, price_calculator):
        # Test with prices that would cause floating point precision issues
        product_catalog.products["precise_item"] = {"base_price": 9.99, "category": "test"}
        
        result = product_catalog.get_product_price("precise_item", apply_discount=True)
        # 9.99 + (9.99 * 0.1) - (9.99 * 0.05) = 9.99 + 0.999 - 0.4995 = 10.4895 → rounds to 10.49
        assert result == 10.49
        assert isinstance(result, float)
    
    # DATA FLOW ACCURACY TESTS
    
    def test_sequential_calls_maintain_state(self, product_catalog, price_calculator):
        # Make multiple calls and ensure calculator state is maintained
        with patch.object(price_calculator, 'calculate_final_price', wraps=price_calculator.calculate_final_price) as mock_calc:
            product_catalog.get_product_price("laptop", apply_discount=False)
            product_catalog.get_product_price("book", apply_discount=True)
            
            # Verify all calls happened with correct parameters
            assert mock_calc.call_count == 2
            expected_calls = [
                call(1000, apply_tax=True, apply_discount=False),
                call(20, apply_tax=True, apply_discount=True)
            ]
            mock_calc.assert_has_calls(expected_calls, any_order=False)
    
    def test_calculator_parameter_modification(self, product_catalog, price_calculator):
        # Modify calculator parameters between calls
        laptop_price_before = product_catalog.get_product_price("laptop", apply_discount=False)
        
        # Change calculator parameters
        price_calculator.tax_rate = 0.2
        
        laptop_price_after = product_catalog.get_product_price("laptop", apply_discount=False)
        
        # Verify that the change in calculator affected the result
        assert laptop_price_before == 1100  # 1000 + 10%
        assert laptop_price_after == 1200  # 1000 + 20%