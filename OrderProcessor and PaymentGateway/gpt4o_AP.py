import pytest
from unittest.mock import Mock, patch
from OrderProcessor import OrderProcessor
from PaymentGateway import PaymentGateway

class TestOrderProcessorIntegration:
    @pytest.fixture
    def payment_gateway(self):
        return PaymentGateway()
    
    @pytest.fixture
    def order_processor(self, payment_gateway):
        return OrderProcessor(payment_gateway)
    
    def test_successful_order_creation(self, order_processor):
        # Arrange
        items = ["item1", "item2"]
        total = 100.00
        valid_card = "1234567890123456"
        
        # Act
        order_id = order_processor.create_order(items, total, valid_card)
        
        # Assert
        assert order_id is not None
        assert order_id == "ORD-1"
        assert order_processor.orders[order_id]["total"] == total
        assert order_processor.orders[order_id]["items"] == items
        assert order_processor.orders[order_id]["transaction_id"] == "TX-1"
    
    def test_invalid_card_number(self, order_processor):
        # Arrange
        items = ["item1"]
        total = 50.00
        invalid_card = "123"  # Invalid card number
        
        # Act
        order_id = order_processor.create_order(items, total, invalid_card)
        
        # Assert
        assert order_id is None
        assert len(order_processor.orders) == 0
        assert len(order_processor.payment_gateway.transactions) == 0
    
    def test_multiple_orders_creation(self, order_processor):
        # Arrange
        valid_card = "1234567890123456"
        
        # Act
        order_id1 = order_processor.create_order(["item1"], 100.00, valid_card)
        order_id2 = order_processor.create_order(["item2"], 200.00, valid_card)
        
        # Assert
        assert order_id1 == "ORD-1"
        assert order_id2 == "ORD-2"
        assert len(order_processor.orders) == 2
        assert len(order_processor.payment_gateway.transactions) == 2
        assert order_processor.payment_gateway.transactions[0]["amount"] == 100.00
        assert order_processor.payment_gateway.transactions[1]["amount"] == 200.00
    
    def test_transaction_data_storage(self, order_processor):
        # Arrange
        items = ["expensive item"]
        total = 999.99
        card_number = "9876543210987654"
        
        # Act
        order_id = order_processor.create_order(items, total, card_number)
        
        # Assert
        transaction = order_processor.payment_gateway.transactions[0]
        assert transaction["amount"] == total
        assert transaction["card"] == "7654"  # Last 4 digits
        assert transaction["id"] == order_processor.orders[order_id]["transaction_id"]
    
    def test_non_digit_card_number(self, order_processor):
        # Arrange
        items = ["item1"]
        total = 50.00
        invalid_card = "123456789012345A"  # Non-digit character
        
        # Act
        order_id = order_processor.create_order(items, total, invalid_card)
        
        # Assert
        assert order_id is None
        assert len(order_processor.orders) == 0
        
    def test_order_reference_integrity(self, order_processor):
        # Arrange
        valid_card = "1234567890123456"
        
        # Act
        order_processor.create_order(["item1"], 100.00, valid_card)
        order_processor.create_order(["item2"], 200.00, valid_card)
        
        # Assert
        assert order_processor.orders["ORD-1"]["transaction_id"] == "TX-1"
        assert order_processor.orders["ORD-2"]["transaction_id"] == "TX-2"
    
    def test_partial_failure_payment_gateway(self, order_processor):
        # Arrange
        items = ["item1"]
        total = 50.00
        valid_card = "1234567890123456"
        
        with patch.object(PaymentGateway, 'process_payment', return_value=None):
            # Act
            order_id = order_processor.create_order(items, total, valid_card)
            
            # Assert
            assert order_id is None
            assert len(order_processor.orders) == 0
            assert len(order_processor.payment_gateway.transactions) == 0
    
    def test_edge_case_empty_items(self, order_processor):
        # Arrange
        items = []
        total = 0.00
        valid_card = "1234567890123456"
        
        # Act
        order_id = order_processor.create_order(items, total, valid_card)
        
        # Assert
        assert order_id is not None
        assert order_id == "ORD-1"
        assert order_processor.orders[order_id]["total"] == total
        assert order_processor.orders[order_id]["items"] == items
        assert order_processor.orders[order_id]["transaction_id"] == "TX-1"