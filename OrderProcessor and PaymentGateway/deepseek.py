import pytest
from unittest.mock import MagicMock
from OrderProcessor import OrderProcessor
from PaymentGateway import PaymentGateway

class TestIntegrationOrderProcessor:
    def setup_method(self):
        self.mock_gateway = MagicMock(spec=PaymentGateway)
        self.processor = OrderProcessor(self.mock_gateway)

    def test_successful_order_creation(self):
        self.mock_gateway.process_payment.return_value = "TX-123"
        
        order_id = self.processor.create_order(["item1", "item2"], 100.0, "4111111111111111")
        
        assert order_id.startswith("ORD-")
        assert self.processor.orders[order_id]["transaction_id"] == "TX-123"
        self.mock_gateway.process_payment.assert_called_once_with(100.0, "4111111111111111")

    def test_payment_failure_handling(self):
        self.mock_gateway.process_payment.return_value = None
        
        order_id = self.processor.create_order(["item3"], 50.0, "invalid_card")
        assert order_id is None
        assert len(self.processor.orders) == 0

    def test_payment_gateway_error_propagation(self):
        self.mock_gateway.process_payment.side_effect = Exception("Gateway timeout")
        
        with pytest.raises(Exception) as exc_info:
            self.processor.create_order([], 0.0, "4111111111111111")
        assert "Gateway timeout" in str(exc_info.value)

    def test_edge_case_invalid_card_length(self):
        self.mock_gateway.process_payment.return_value = None
        
        assert self.processor.create_order(["item4"], 75.0, "1234") is None
        self.mock_gateway.process_payment.assert_called_once_with(75.0, "1234")

    def test_real_integration_flow(self):
        real_gateway = PaymentGateway()
        processor = OrderProcessor(real_gateway)
        
        valid_order_id = processor.create_order(["book"], 29.99, "1234567890123456")
        assert valid_order_id is not None
        assert real_gateway.transactions[0]["id"].startswith("TX-")
        
        invalid_order_id = processor.create_order(["pen"], 5.0, "bad_card")
        assert invalid_order_id is None