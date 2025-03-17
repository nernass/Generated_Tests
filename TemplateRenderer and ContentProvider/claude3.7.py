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

def test_render_homepage(template_renderer):
    result = template_renderer.render("homepage")
    assert result == "<h1>Welcome to our site</h1><p>This is the homepage content</p>"

def test_render_about(template_renderer):
    result = template_renderer.render("about")
    assert result == "<div class='about'><h2>About Us</h2><div>We are a company that does things</div></div>"

def test_render_nonexistent_page(template_renderer):
    result = template_renderer.render("contact")
    assert result == "Page not found"

def test_content_provider_integration():
    # Test that the template renderer correctly uses content from provider
    content_provider = ContentProvider()
    template_renderer = TemplateRenderer(content_provider)
    
    result = template_renderer.render("homepage")
    assert "Welcome to our site" in result
    assert "This is the homepage content" in result

def test_mocked_content_provider():
    # Test with mocked content provider to verify integration
    mock_provider = Mock()
    mock_provider.get_content.return_value = {"title": "Test Title", "body": "Test Body"}
    
    renderer = TemplateRenderer(mock_provider)
    result = renderer.render("homepage")
    
    assert "Test Title" in result
    assert "Test Body" in result
    mock_provider.get_content.assert_called_once_with("homepage")

def test_partial_content():
    # Test how the integration handles partial content
    mock_provider = Mock()
    mock_provider.get_content.return_value = {"title": "Only Title"}
    
    renderer = TemplateRenderer(mock_provider)
    
    with pytest.raises(KeyError):
        renderer.render("about")

def test_none_content():
    # Test that None content from provider is handled correctly
    mock_provider = Mock()
    mock_provider.get_content.return_value = None
    
    renderer = TemplateRenderer(mock_provider)
    result = renderer.render("any-page")
    
    assert result == "Page not found"