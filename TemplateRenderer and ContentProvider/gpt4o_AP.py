import pytest
from unittest.mock import Mock, patch
from TemplateRenderer import TemplateRenderer
from ContentProvider import ContentProvider

class TestContentProviderTemplateRendererIntegration:
    @pytest.fixture
    def content_provider(self):
        return ContentProvider()
    
    @pytest.fixture
    def template_renderer(self, content_provider):
        return TemplateRenderer(content_provider)
    
    # Success path tests
    def test_end_to_end_homepage_render(self, template_renderer):
        """Scenario 1: Valid input with successful component interaction - homepage"""
        result = template_renderer.render("homepage")
        assert result == "<h1>Welcome to our site</h1><p>This is the homepage content</p>"
    
    def test_end_to_end_about_render(self, template_renderer):
        """Scenario 1: Valid input with successful component interaction - about page"""
        result = template_renderer.render("about")
        assert result == "<div class='about'><h2>About Us</h2><div>We are a company that does things</div></div>"
    
    # Failure path tests
    def test_content_provider_fails(self):
        """Scenario 2: Content provider fails"""
        mock_provider = Mock()
        mock_provider.get_content.side_effect = Exception("Database connection failed")
        renderer = TemplateRenderer(mock_provider)
        
        # Since the application doesn't have error handling for this case,
        # we expect the exception to propagate
        with pytest.raises(Exception) as exc_info:
            renderer.render("homepage")
        assert "Database connection failed" in str(exc_info.value)
    
    def test_content_provider_returns_none(self):
        """Scenario 2: Content provider returns None for non-existent page"""
        mock_provider = Mock()
        mock_provider.get_content.return_value = None
        renderer = TemplateRenderer(mock_provider)
        
        result = renderer.render("nonexistent")
        assert result == "Page not found"
        mock_provider.get_content.assert_called_once_with("nonexistent")
    
    # Edge cases
    def test_empty_page_name(self, template_renderer):
        """Scenario 3: Empty page name"""
        result = template_renderer.render("")
        assert result == "Page not found"
    
    def test_none_page_name(self, template_renderer):
        """Scenario 3: None page name"""
        result = template_renderer.render(None)
        assert result == "Page not found"
    
    def test_malformed_content(self):
        """Edge case: Content missing required fields"""
        mock_provider = Mock()
        mock_provider.get_content.return_value = {"title": "Only Title"}  # missing body
        renderer = TemplateRenderer(mock_provider)
        
        with pytest.raises(KeyError):
            renderer.render("homepage")
    
    def test_content_exists_but_template_missing(self):
        """Edge case: Content exists but template doesn't"""
        mock_provider = Mock()
        mock_provider.get_content.return_value = {"title": "Custom", "body": "Content"}
        renderer = TemplateRenderer(mock_provider)
        
        result = renderer.render("custom_page")  # page not in templates dict
        assert result == "Page not found"
    
    # Data flow tests
    def test_content_provider_correct_input(self):
        """Verify ContentProvider receives correct input from TemplateRenderer"""
        mock_provider = Mock()
        mock_provider.get_content.return_value = {"title": "Test", "body": "Content"}
        renderer = TemplateRenderer(mock_provider)
        
        renderer.render("test_page")
        mock_provider.get_content.assert_called_once_with("test_page")
    
    def test_template_renderer_uses_content_correctly(self):
        """Verify TemplateRenderer uses content from ContentProvider correctly"""
        mock_provider = Mock()
        test_content = {"title": "Custom Title", "body": "Custom Body"}
        mock_provider.get_content.return_value = test_content
        renderer = TemplateRenderer(mock_provider)
        
        result = renderer.render("homepage")
        assert result == "<h1>Custom Title</h1><p>Custom Body</p>"
    
    # Extended tests with patching
    @patch.dict('ContentProvider.ContentProvider.content', {
        "custom": {"title": "Patched Title", "body": "Patched Body"}
    }, clear=False)
    def test_with_extended_content(self, content_provider):
        """Test with extended content through patching"""
        renderer = TemplateRenderer(content_provider)
        # Add a custom template for this test
        renderer.templates["custom"] = "<article>{title}: {body}</article>"
        
        result = renderer.render("custom")
        assert result == "<article>Patched Title: Patched Body</article>"