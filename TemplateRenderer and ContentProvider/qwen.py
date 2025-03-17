import pytest
from unittest.mock import MagicMock

class ContentProvider:
    def __init__(self):
        self.content = {
            "homepage": {
                "title": "Welcome to our site",
                "body": "This is the homepage content"
            },
            "about": {
                "title": "About Us",
                "body": "We are a company that does things"
            }
        }
        
    def get_content(self, page_name):
        return self.content.get(page_name)

class TemplateRenderer:
    def __init__(self, content_provider):
        self.content_provider = content_provider
        self.templates = {
            "homepage": "<h1>{title}</h1><p>{body}</p>",
            "about": "<div class='about'><h2>{title}</h2><div>{body}</div></div>"
        }
        
    def render(self, page_name):
        content = self.content_provider.get_content(page_name)
        template = self.templates.get(page_name)
        
        if content and template:
            return template.format(**content)
        return "Page not found"

@pytest.fixture
def content_provider():
    return ContentProvider()

@pytest.fixture
def template_renderer(content_provider):
    return TemplateRenderer(content_provider)

class TestIntegrationContentProviderAndTemplateRenderer:

    def test_success_path_render_homepage(self, template_renderer):
        result = template_renderer.render("homepage")
        expected = "<h1>Welcome to our site</h1><p>This is the homepage content</p>"
        assert result == expected

    def test_success_path_render_about(self, template_renderer):
        result = template_renderer.render("about")
        expected = "<div class='about'><h2>About Us</h2><div>We are a company that does things</div></div>"
        assert result == expected

    def test_partial_failure_content_provider_returns_none(self, template_renderer, content_provider):
        content_provider.get_content = MagicMock(return_value=None)
        result = template_renderer.render("homepage")
        assert result == "Page not found"

    def test_partial_failure_template_renderer_missing_template(self, template_renderer, content_provider):
        template_renderer.templates = {}
        result = template_renderer.render("homepage")
        assert result == "Page not found"

    def test_edge_case_page_name_not_found(self, template_renderer):
        result = template_renderer.render("nonexistent")
        assert result == "Page not found"

    def test_edge_case_empty_page_name(self, template_renderer):
        result = template_renderer.render("")
        assert result == "Page not found"

    def test_edge_case_special_characters_in_page_name(self, template_renderer):
        result = template_renderer.render("!@#")
        assert result == "Page not found"

    def test_edge_case_large_page_name(self, template_renderer):
        large_page_name = "a" * 100
        result = template_renderer.render(large_page_name)
        assert result == "Page not found"

    def test_edge_case_content_provider_raises_exception(self, template_renderer, content_provider):
        content_provider.get_content = MagicMock(side_effect=Exception("ContentProvider error"))
        with pytest.raises(Exception) as excinfo:
            template_renderer.render("homepage")
        assert str(excinfo.value) == "ContentProvider error"

    def test_edge_case_template_renderer_raises_exception(self, template_renderer, content_provider):
        template_renderer.templates = {
            "homepage": "<h1>{title}</h1><p>{body}</p>"
        }
        content_provider.get_content = MagicMock(return_value={"title": "Welcome", "body": "Content"})
        template_renderer.templates["homepage"] = MagicMock(side_effect=Exception("TemplateRenderer error"))
        with pytest.raises(Exception) as excinfo:
            template_renderer.render("homepage")
        assert str(excinfo.value) == "TemplateRenderer error"

    def test_edge_case_content_with_missing_keys(self, template_renderer, content_provider):
        content_provider.content = {
            "homepage": {
                "title": "Welcome to our site"
            }
        }
        result = template_renderer.render("homepage")
        assert result == "Page not found"

    def test_edge_case_content_with_extra_keys(self, template_renderer, content_provider):
        content_provider.content = {
            "homepage": {
                "title": "Welcome to our site",
                "body": "This is the homepage content",
                "extra": "Extra info"
            }
        }
        result = template_renderer.render("homepage")
        expected = "<h1>Welcome to our site</h1><p>This is the homepage content</p>"
        assert result == expected

    def test_edge_case_template_with_missing_placeholders(self, template_renderer, content_provider):
        template_renderer.templates = {
            "homepage": "<h1>{title}</h1><p>{missing}</p>"
        }
        result = template_renderer.render("homepage")
        assert result == "Page not found"

    def test_edge_case_template_with_extra_placeholders(self, template_renderer, content_provider):
        template_renderer.templates = {
            "homepage": "<h1>{title}</h1><p>{body}</p><div>{extra}</div>"
        }
        result = template_renderer.render("homepage")
        assert result == "Page not found"

    def test_edge_case_content_provider_returns_empty_dict(self, template_renderer, content_provider):
        content_provider.get_content = MagicMock(return_value={})
        result = template_renderer.render("homepage")
        assert result == "Page not found"

    def test_edge_case_content_provider_returns_invalid_type(self, template_renderer, content_provider):
        content_provider.get_content = MagicMock(return_value="Invalid content")
        result = template_renderer.render("homepage")
        assert result == "Page not found"