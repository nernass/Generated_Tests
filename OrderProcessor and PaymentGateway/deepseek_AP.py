import pytest
from unittest.mock import MagicMock
from OrderProcessor import OrderProcessor
from PaymentGateway import PaymentGateway

class TestIntegrationOrderProcessor:
    def setup_method(self):
        self.mock_gateway = MagicMock(spec=PaymentGateway)
        self.processor = OrderProcessor(self.mock_gateway)

    def test_successful_order_creation_flow(self):
        self.mock_gateway.process_payment.return_value = "TX-100"
        
        order_id = self.processor.create_order(["Laptop", "Mouse"], 1500.0, "4111222233334444")
        
        assert order_id.startswith("ORD-")
        assert self.processor.orders[order_id]["total"] == 1500.0
        self.mock_gateway.process_payment.assert_called_once_with(1500.0, "4111222233334444")

    def test_payment_failure_blocks_order(self):
        self.mock_gateway.process_payment.return_value = None
        
        order_id = self.processor.create_order(["Keyboard"], 99.99, "invalid123")
        
        assert order_id is None
        assert len(self.processor.orders) == 0
        self.mock_gateway.process_payment.assert_called_once_with(99.99, "invalid123")

    def test_gateway_exception_propagation(self):
        self.mock_gateway.process_payment.side_effect = ConnectionError("API timeout")
        
        with pytest.raises(ConnectionError) as exc_info:
            self.processor.create_order([], 0.0, "4111111111111111")
        assert "API timeout" in str(exc_info.value)
        assert len(self.processor.orders) == 0

    def test_edge_case_zero_amount_order(self):
        self.mock_gateway.process_payment.return_value = "TX-0"
        
        order_id = self.processor.create_order([], 0.0, "0000000000000000")
        
        assert order_id is not None
        self.mock_gateway.process_payment.assert_called_once_with(0.0, "0000000000000000")

    def test_invalid_card_length_handling(self):
        self.mock_gateway.process_payment.return_value = None
        
        assert self.processor.create_order(["Monitor"], 300.0, "1234") is None
        self.mock_gateway.process_payment.assert_called_once_with(300.0, "1234")

    def test_real_integration_with_gateway(self):
        real_gateway = PaymentGateway()
        processor = OrderProcessor(real_gateway)
        
        valid_id = processor.create_order(["Tablet"], 299.99, "1234567890123456")
        invalid_id = processor.create_order(["Pen"], 2.99, "bad_card")
        
        assert valid_id.startswith("ORD-")
        assert real_gateway.transactions[0]["id"] == "TX-1"
        assert invalid_id is None
        assert len(real_gateway.transactions) == 1