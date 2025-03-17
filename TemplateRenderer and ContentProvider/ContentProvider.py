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
