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
            "body": "Test Body"
        }
        result = self.renderer.render("homepage")
        assert "<h1>Test Title</h1>" in result
        assert "<p>Test Body</p>" in result
        self.mock_provider.get_content.assert_called_once_with("homepage")

    def test_missing_content_handling(self):
        self.mock_provider.get_content.return_value = None
        assert self.renderer.render("invalid_page") == "Page not found"

    def test_missing_template_handling(self):
        self.mock_provider.get_content.return_value = {
            "title": "Contact",
            "body": "Contact info"
        }
        assert self.renderer.render("contact") == "Page not found"

    def test_content_provider_failure_propagation(self):
        self.mock_provider.get_content.side_effect = ValueError("DB error")
        with pytest.raises(ValueError) as exc_info:
            self.renderer.render("about")
        assert "DB error" in str(exc_info.value)

    def test_real_integration_flow(self):
        real_provider = ContentProvider()
        renderer = TemplateRenderer(real_provider)
        
        homepage = renderer.render("homepage")
        assert "<h1>Welcome to our site</h1>" in homepage
        assert "homepage content" in homepage
        
        about_page = renderer.render("about")
        assert "<h2>About Us</h2>" in about_page
        assert "company that does things" in about_page
        
        assert renderer.render("invalid") == "Page not found"