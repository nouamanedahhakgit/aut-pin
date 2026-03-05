import re
from pathlib import Path

for p in Path('articles-website-generator/generators').glob('generator-*.py'):
    if p.name in ['generator-1.py', 'generator-2.py', 'generator-4.py', 'generator-8.py']: 
        continue
    
    text = p.read_text(encoding='utf-8')
    
    # Replace cat = ... with from ai_client import get_first_category; cat = get_first_category(self.config)
    new_text = re.sub(
        r'cat\s*=\s*self\.config\["categories_list"\]\[0\] if self\.config\["categories_list"\] else \{.*?\}.*\n',
        'from ai_client import get_first_category\n        cat = get_first_category(self.config)\n',
        text
    )
    
    if new_text != text:
        p.write_text(new_text, encoding='utf-8')
        print(f'Updated {p.name}')
