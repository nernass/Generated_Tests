import pytest
from unittest.mock import Mock, patch
from TemplateRenderer import TemplateRenderer
from ContentProvider import ContentProvider

class TestContentProviderTemplateRendererIntegration:
    @pytest.fixture
    def default_content_provider(self):
        return ContentProvider()

    @pytest.fixture
    def template_renderer(self, default_content_provider):
        return TemplateRenderer(default_content_provider)

    def test_success_path(self, template_renderer):
        """Scenario 1: Valid input with successful component interaction"""
        result = template_renderer.render("homepage")
        assert result == "<h1>Welcome to our site</h1><p>This is the homepage content</p>"

    def test_component_failure(self):
        """Scenario 2: Component failure handling"""
        mock_provider = Mock()
        mock_provider.get_content.side_effect = Exception("Database connection failed")
        renderer = TemplateRenderer(mock_provider)

        with pytest.raises(Exception) as exc_info:
            renderer.render("homepage")
        assert str(exc_info.value) == "Database connection failed"

    def test_invalid_input(self, template_renderer):
        """Scenario 3: Invalid input handling"""
        result = template_renderer.render("")
        assert result == "Page not found"

    def test_data_flow_accuracy(self):
        """Verify correct data flow between components"""
        mock_provider = Mock()
        mock_provider.get_content.return_value = {
            "title": "Test Title",
            "body": "Test Body"
        }
        renderer = TemplateRenderer(mock_provider)

        result = renderer.render("homepage")
        
        mock_provider.get_content.assert_called_once_with("homepage")
        assert result == "<h1>Test Title</h1><p>Test Body</p>"

    def test_missing_template(self, default_content_provider):
        """Edge case: Content exists but template doesn't"""
        renderer = TemplateRenderer(default_content_provider)
        result = renderer.render("non_existent_template")
        assert result == "Page not found"

    def test_malformed_content(self):
        """Edge case: Malformed content from provider"""
        mock_provider = Mock()
        mock_provider.get_content.return_value = {"title": "Incomplete Data"}
        renderer = TemplateRenderer(mock_provider)

        with pytest.raises(KeyError):
            renderer.render("homepage")

    def test_null_content(self):
        """Edge case: Null content from provider"""
        mock_provider = Mock()
        mock_provider.get_content.return_value = None
        renderer = TemplateRenderer(mock_provider)

        result = renderer.render("any_page")
        assert result == "Page not found"

    @patch('ContentProvider.ContentProvider')
    def test_provider_retry_mechanism(self, mock_provider_class):
        """Test retry mechanism on temporary failures"""
        mock_provider = mock_provider_class.return_value
        mock_provider.get_content.side_effect = [
            Exception("Temporary failure"),
            {"title": "Success", "body": "After retry"}
        ]
        
        renderer = TemplateRenderer(mock_provider)
        result = renderer.render("homepage")
        
        assert mock_provider.get_content.call_count == 2
        assert result == "<h1>Success</h1><p>After retry</p>"