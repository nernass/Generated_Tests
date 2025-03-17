import pytest
from unittest.mock import Mock, patch
import sys
import os
from PaymentGateway import PaymentGateway
from OrderProcessor import OrderProcessor

class TestOrderProcessorIntegration:
    @pytest.fixture
    def payment_gateway(self):
        return PaymentGateway()
    
    @pytest.fixture
    def order_processor(self, payment_gateway):
        return OrderProcessor(payment_gateway)
    
    # Success path tests
    
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
    
    def test_data_flow_between_components(self, order_processor):
        # Arrange
        items = ["laptop"]
        total = 999.99
        card_number = "9876543210987654"
        
        # Act
        with patch.object(order_processor.payment_gateway, 'process_payment', wraps=order_processor.payment_gateway.process_payment) as mocked_payment:
            order_id = order_processor.create_order(items, total, card_number)
            
            # Assert data flow accuracy
            mocked_payment.assert_called_once_with(total, card_number)
            assert order_processor.orders[order_id]["transaction_id"] == "TX-1"
            assert order_processor.payment_gateway.transactions[0]["amount"] == total
            assert order_processor.payment_gateway.transactions[0]["card"] == "7654"
    
    # Failure path tests
    
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
    
    def test_payment_gateway_failure(self, order_processor):
        # Arrange
        items = ["item1"]
        total = 50.00
        valid_card = "1234567890123456"
        
        # Mock payment gateway to fail
        with patch.object(order_processor.payment_gateway, 'process_payment', return_value=None) as mock_payment:
            # Act
            order_id = order_processor.create_order(items, total, valid_card)
            
            # Assert
            mock_payment.assert_called_once_with(total, valid_card)