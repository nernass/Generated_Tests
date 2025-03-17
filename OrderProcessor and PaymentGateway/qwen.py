import pytest
from unittest.mock import MagicMock

class OrderProcessor:
    def __init__(self, payment_gateway):
        self.orders = {}
        self.payment_gateway = payment_gateway
        
    def create_order(self, items, total, card_number):
        transaction_id = self.payment_gateway.process_payment(total, card_number)
        if transaction_id:
            order_id = f"ORD-{len(self.orders) + 1}"
            self.orders[order_id] = {"items": items, "total": total, "transaction_id": transaction_id}
            return order_id
        return None

class PaymentGateway:
    def __init__(self):
        self.transactions = []
        
    def process_payment(self, amount, card_number):
        if len(card_number) == 16 and card_number.isdigit():
            transaction_id = f"TX-{len(self.transactions) + 1}"
            self.transactions.append({"id": transaction_id, "amount": amount, "card": card_number[-4:]})
            return transaction_id
        return None

@pytest.fixture
def payment_gateway():
    return PaymentGateway()

@pytest.fixture
def order_processor(payment_gateway):
    return OrderProcessor(payment_gateway)

class TestIntegrationOrderProcessorAndPaymentGateway:

    def test_success_path_create_order_with_valid_payment(self, order_processor, payment_gateway):
        items = ["item1", "item2"]
        total = 100.0
        card_number = "1234567890123456"
        order_id = order_processor.create_order(items, total, card_number)
        assert order_id == "ORD-1"
        assert order_processor.orders[order_id] == {"items": items, "total": total, "transaction_id": "TX-1"}
        assert payment_gateway.transactions[0] == {"id": "TX-1", "amount": 100.0, "card": "3456"}

    def test_partial_failure_invalid_card_number(self, order_processor, payment_gateway):
        items = ["item1", "item2"]
        total = 100.0
        card_number = "123456789012345"  # Invalid card number (not 16 digits)
        order_id = order_processor.create_order(items, total, card_number)
        assert order_id is None
        assert order_processor.orders == {}
        assert payment_gateway.transactions == []

    def test_partial_failure_payment_gateway_throws_exception(self, order_processor, payment_gateway):
        payment_gateway.process_payment = MagicMock(side_effect=Exception("Payment gateway error"))
        items = ["item1", "item2"]
        total = 100.0
        card_number = "1234567890123456"
        with pytest.raises(Exception) as excinfo:
            order_processor.create_order(items, total, card_number)
        assert str(excinfo.value) == "Payment gateway error"
        assert order_processor.orders == {}
        assert payment_gateway.transactions == []

    def test_edge_case_zero_total_amount(self, order_processor, payment_gateway):
        items = ["item1", "item2"]
        total = 0.0
        card_number = "1234567890123456"
        order_id = order_processor.create_order(items, total, card_number)
        assert order_id is None
        assert order_processor.orders == {}
        assert payment_gateway.transactions == []

    def test_edge_case_large_total_amount(self, order_processor, payment_gateway):
        items = ["item1", "item2"]
        total = 1000000000.0
        card_number = "1234567890123456"
        order_id = order_processor.create_order(items, total, card_number)
        assert order_id == "ORD-1"
        assert order_processor.orders[order_id] == {"items": items, "total": total, "transaction_id": "TX-1"}
        assert payment_gateway.transactions[0] == {"id": "TX-1", "amount": 1000000000.0, "card": "3456"}

    def test_edge_case_empty_items_list(self, order_processor, payment_gateway):
        items = []
        total = 100.0
        card_number = "1234567890123456"
        order_id = order_processor.create_order(items, total, card_number)
        assert order_id == "ORD-1"
        assert order_processor.orders[order_id] == {"items": items, "total": total, "transaction_id": "TX-1"}
        assert payment_gateway.transactions[0] == {"id": "TX-1", "amount": 100.0, "card": "3456"}

    def test_edge_case_special_characters_in_card_number(self, order_processor, payment_gateway):
        items = ["item1", "item2"]
        total = 100.0
        card_number = "1234-5678-9012-3456"  # Invalid card number (contains special characters)
        order_id = order_processor.create_order(items, total, card_number)
        assert order_id is None
        assert order_processor.orders == {}
        assert payment_gateway.transactions == []