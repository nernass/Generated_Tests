import pytest
from unittest.mock import Mock
from TemplateRenderer import TemplateRenderer
from ContentProvider import ContentProvider

@pytest.fixture
def content_provider():
    return ContentProvider()

@pytest.fixture
def template_renderer(content_provider):
    return TemplateRenderer(content_provider)

class TestTemplateRendererIntegration:
    def test_successful_page_render(self, template_renderer):
        # Test happy path with existing page
        result = template_renderer.render("homepage")
        assert result == "<h1>Welcome to our site</h1><p>This is the homepage content</p>"
    
    def test_different_template_layout(self, template_renderer):
        # Test different template structure
        result = template_renderer.render("about")
        assert result == "<div class='about'><h2>About Us</h2><div>We are a company that does things</div></div>"

    def test_missing_page_handling(self, template_renderer):
        # Test non-existent page
        result = template_renderer.render("nonexistent")
        assert result == "Page not found"

    def test_custom_content_integration(self):
        # Test with custom content provider implementation
        mock_provider = Mock()
        mock_provider.get_content.return_value = {
            "title": "Custom Title",
            "body": "Custom Body"
        }
        custom_renderer = TemplateRenderer(mock_provider)
        
        result = custom_renderer.render("homepage")
        assert result == "<h1>Custom Title</h1><p>Custom Body</p>"
        mock_provider.get_content.assert_called_once_with("homepage")

    def test_invalid_content_format(self):
        # Test handling of malformed content
        mock_provider = Mock()
        mock_provider.get_content.return_value = {"title": "Only Title"}
        renderer = TemplateRenderer(mock_provider)
        
        with pytest.raises(KeyError):
            renderer.render("homepage")

    def test_none_content_handling(self):
        # Test handling of None content
        mock_provider = Mock()
        mock_provider.get_content.return_value = None
        renderer = TemplateRenderer(mock_provider)
        
        result = renderer.render("any-page")
        assert result == "Page not found"