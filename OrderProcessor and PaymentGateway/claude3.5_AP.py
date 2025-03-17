import pytest
from unittest.mock import Mock, patch
import logging
from PaymentGateway import PaymentGateway
from OrderProcessor import OrderProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestOrderProcessorIntegration:
    @pytest.fixture
    def mock_payment_gateway(self):
        return Mock(spec=PaymentGateway)

    @pytest.fixture
    def payment_gateway(self):
        return PaymentGateway()
    
    @pytest.fixture
    def order_processor(self, payment_gateway):
        return OrderProcessor(payment_gateway)

    # Scenario 1: Success Path Tests
    def test_successful_order_flow(self, order_processor):
        # Arrange
        items = ["item1", "item2"]
        total = 100.00
        valid_card = "1234567890123456"
        
        # Act
        with patch.object(order_processor.payment_gateway, 'process_payment', wraps=order_processor.payment_gateway.process_payment) as mock_payment:
            order_id = order_processor.create_order(items, total, valid_card)
            
            # Assert
            assert order_id == "ORD-1"
            mock_payment.assert_called_once_with(total, valid_card)
            assert order_processor.orders[order_id]["transaction_id"] == "TX-1"
            assert order_processor.payment_gateway.transactions[0]["amount"] == total
            assert order_processor.payment_gateway.transactions[0]["card"] == "3456"

    # Scenario 2: Component Failure Tests
    def test_payment_gateway_failure(self, order_processor):
        # Arrange
        items = ["item1"]
        total = 50.00
        valid_card = "1234567890123456"
        
        # Act
        with patch.object(order_processor.payment_gateway, 'process_payment', return_value=None) as mock_payment:
            order_id = order_processor.create_order(items, total, valid_card)
            
            # Assert
            assert order_id is None
            mock_payment.assert_called_once()
            assert len(order_processor.orders) == 0

    def test_payment_gateway_exception(self, order_processor):
        # Arrange
        items = ["item1"]
        total = 50.00
        valid_card = "1234567890123456"
        
        # Act
        with patch.object(order_processor.payment_gateway, 'process_payment', side_effect=Exception("Payment service error")) as mock_payment:
            with pytest.raises(Exception) as exc_info:
                order_processor.create_order(items, total, valid_card)
            
            # Assert
            assert "Payment service error" in str(exc_info.value)
            mock_payment.assert_called_once()
            assert len(order_processor.orders) == 0

    # Scenario 3: Invalid Input Tests
    def test_invalid_card_number_propagation(self, order_processor):
        # Arrange
        items = ["item1"]
        total = 50.00
        invalid_cards = ["123", "123456789012345A", "", "1234567890123456789"]
        
        # Act & Assert
        for card in invalid_cards:
            order_id = order_processor.create_order(items, total, card)
            assert order_id is None
            assert len(order_processor.orders) == 0
            assert len(order_processor.payment_gateway.transactions) == 0

    # Edge Cases
    def test_edge_case_zero_amount(self, order_processor):
        # Arrange
        items = []
        total = 0.00
        valid_card = "1234567890123456"
        
        # Act
        order_id = order_processor.create_order(items, total, valid_card)
        
        # Assert
        assert order_id is not None
        assert order_processor.orders[order_id]["total"] == 0.00
        assert order_processor.payment_gateway.transactions[0]["amount"] == 0.00

    def test_edge_case_negative_amount(self, order_processor):
        # Arrange
        items = ["refund"]
        total = -50.00
        valid_card = "1234567890123456"
        
        # Act
        order_id = order_processor.create_order(items, total, valid_card)
        
        # Assert
        assert order_id is not None
        assert order_processor.orders[order_id]["total"] == -50.00
        assert order_processor.payment_gateway.transactions[0]["amount"] == -50.00

    def test_data_integrity_across_components(self, order_processor):
        # Arrange
        items = ["item1", "item2"]
        totals = [100.00, 200.00]
        valid_card = "1234567890123456"
        
        # Act
        order_ids = []
        for total in totals:
            order_id = order_processor.create_order(items, total, valid_card)
            order_ids.append(order_id)
        
        # Assert
        for i, order_id in enumerate(order_ids):
            assert order_processor.orders[order_id]["total"] == totals[i]
            assert order_processor.orders[order_id]["transaction_id"] == f"TX-{i+1}"
            assert order_processor.payment_gateway.transactions[i]["amount"] == totals[i]