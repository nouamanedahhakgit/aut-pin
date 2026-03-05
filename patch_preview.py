import re
from pathlib import Path

def patch_file(p):
    text = p.read_text(encoding="utf-8")
    if "def run_preview(" in text:
        return
    
    # Check if there's a structure like build_content_data (generators 4, 8, 9) or just generate_html
    if "def build_content_data" in text:
        # For generator-8 and generator-9, we can mock the data dictionary
        # We will handle these individually or patch run() directly
        pass
    
    match = re.search(r"    def run\(self[^\n]*:", text)
    if not match:
        print(f"run() not found in {p.name}")
        return
        
    preview_code = """
    def run_preview(self):
        \"\"\"Generate article template with placeholder content (no AI). For config preview.\"\"\"
        self.title = self.config.get("title", "Sample Recipe")
        self.slug = self._slugify(self.title) if hasattr(self, '_slugify') else self.title.lower().replace(' ', '-')

        intro = "This is a delicious sample recipe that you will absolutely love. It is easy to make and perfect for any occasion."
        why_items = ["It's quick and easy", "Requires minimal ingredients", "Tastes amazing every time"]
        ing_intro = "Gather these simple ingredients to get started."
        ing_list = ["1 cup flour", "2 eggs", "1/2 cup sugar", "1 tsp vanilla", "1/2 tsp salt"]
        steps = [
            {"heading": "Prep", "title": "Prep", "body": "Preheat your oven and prepare the ingredients."},
            {"heading": "Mix", "title": "Mix", "body": "Combine all ingredients in a large bowl until smooth."},
            {"heading": "Bake", "title": "Bake", "body": "Bake for 30 minutes until golden brown."},
        ]
        tips = ["Use room temperature ingredients.", "Don't overmix the batter.", "Measure flour correctly.", "Let it cool completely before slicing."]
        serving = "Serve warm with a scoop of vanilla ice cream."
        conclusion = "We hope you enjoy this recipe as much as we do!"
        faqs = [
            {"question": "Can I make this ahead of time?", "q": "Can I make this ahead of time?", "answer": "Yes, you can make it up to 2 days in advance.", "a": "Yes, you can make it up to 2 days in advance."},
            {"question": "Can I freeze it?", "q": "Can I freeze it?", "answer": "Yes, it freezes beautifully for up to 3 months.", "a": "Yes, it freezes beautifully for up to 3 months."}
        ]
        variations = ["Add chocolate chips", "Use gluten-free flour"]
        storage = "Store in an airtight container for up to 3 days."
        
        recipe = {
            "name": self.title,
            "prep_time": "15 min",
            "cook_time": "30 min",
            "total_time": "45 min",
            "servings": "4",
            "calories": "350 kcal",
            "ingredients": ing_list,
            "instructions": [s["body"] for s in steps]
        }
        
        # We need to mock _gen_recipe if it exists
        original_gen_recipe = getattr(self, "_gen_recipe", None)
        self._gen_recipe = lambda: recipe

        try:
            # Build sections blindly using all possible keys
            sections = [
                {"key": "intro",              "content": intro},
                {"key": "why_i_love_items",   "content": why_items},
                {"key": "why_love_items",     "content": why_items},
                {"key": "why_works_items",    "content": why_items},
                {"key": "ingredients_intro",  "content": ing_intro},
                {"key": "ingredient_list",    "content": ing_list},
                {"key": "ingredients_list",   "content": ing_list},
                {"key": "instructions_steps", "content": steps},
                {"key": "pro_tips",           "content": tips},
                {"key": "serving_suggestions","content": serving},
                {"key": "variations",         "content": variations},
                {"key": "storage",            "content": storage},
                {"key": "conclusion",         "content": conclusion},
                {"key": "faqs",               "content": faqs},
                {"key": "recipe",             "content": recipe},
            ]
            
            # For generator-8, generator-9 which use a data dict:
            if hasattr(self, 'build_content_data'):
                data = {
                    "intro": intro,
                    "why_items": why_items,
                    "ingredients_intro": ing_intro,
                    "ingredients_list": ing_list,
                    "steps": steps,
                    "tips": tips,
                    "serving": serving,
                    "conclusion": conclusion,
                    "faqs": faqs,
                    "recipe": recipe
                }
                html = self.generate_html(data) if "data" in self.generate_html.__code__.co_varnames else self.generate_html(sections)
            else:
                html = self.generate_html(sections)
                
            css = self.generate_css()
    
            return {
                "title": self.title,
                "slug": self.slug,
                "article_html": html,
                "article_css": css
            }
        finally:
            if original_gen_recipe:
                self._gen_recipe = original_gen_recipe
            else:
                del self._gen_recipe

"""
    new_text = text[:match.start()] + preview_code + text[match.start():]
    p.write_text(new_text, encoding="utf-8")
    print(f"Patched {p.name}")

for p in Path("articles-website-generator/generators").glob("generator-*.py"):
    patch_file(p)
