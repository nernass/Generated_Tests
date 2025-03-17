import pytest
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