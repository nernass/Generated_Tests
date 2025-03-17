import pytest
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
        assert order_id.startswith("ORD-")
        assert order_processor.orders[order_id]["total"] == total
        assert order_processor.orders[order_id]["items"] == items
        assert order_processor.orders[order_id]["transaction_id"].startswith("TX-")
    
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