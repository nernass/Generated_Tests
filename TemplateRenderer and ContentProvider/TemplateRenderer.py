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