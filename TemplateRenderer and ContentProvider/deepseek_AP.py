import pytest
from unittest.mock import MagicMock
from ContentProvider import ContentProvider
from TemplateRenderer import TemplateRenderer

class TestIntegrationTemplateRenderer:
    def setup_method(self):
        self.mock_provider = MagicMock(spec=ContentProvider)
        self.renderer = TemplateRenderer(self.mock_provider)

    def test_valid_page_rendering(self):
        self.mock_provider.get_content.return_value = {
            "title": "Test Title",
            "body": "Test Content"
        }
        result = self.renderer.render("homepage")
        assert "<h1>Test Title</h1>" in result
        assert "<p>Test Content</p>" in result
        self.mock_provider.get_content.assert_called_once_with("homepage")

    def test_missing_content_handling(self):
        self.mock_provider.get_content.return_value = None
        assert self.renderer.render("invalid_page") == "Page not found"
        self.mock_provider.get_content.assert_called_once_with("invalid_page")

    def test_missing_template_handling(self):
        self.mock_provider.get_content.return_value = {"title": "Contact", "body": "Details"}
        assert self.renderer.render("contact") == "Page not found"

    def test_content_provider_failure_propagation(self):
        self.mock_provider.get_content.side_effect = RuntimeError("Database unreachable")
        with pytest.raises(RuntimeError) as exc_info:
            self.renderer.render("about")
        assert "Database unreachable" in str(exc_info.value)

    def test_edge_case_empty_content_fields(self):
        self.mock_provider.get_content.return_value = {"title": "", "body": ""}
        result = self.renderer.render("homepage")
        assert "<h1></h1>" in result
        assert "<p></p>" in result

    def test_real_integration_flow(self):
        real_provider = ContentProvider()
        renderer = TemplateRenderer(real_provider)
        
        assert "Welcome to our site" in renderer.render("homepage")
        assert "about" not in renderer.render("invalid_page")
        assert "company that does things" in renderer.render("about")