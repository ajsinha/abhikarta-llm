import os
import re

for i in range(1, 51):
    filename = f"slide{i:02d}.html"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            content = f.read()
        
        # Increase padding on content slides
        content = content.replace('padding: 20px 30px', 'padding: 28px 40px')
        
        # Make header/footer smaller
        content = re.sub(r'margin-bottom: 10px', r'margin-bottom: 8px', content)
        content = re.sub(r'margin-top: 8px', r'margin-top: 6px', content)
        content = re.sub(r'font-size: 7px;([^"]*Copyright)', r'font-size: 6px;\1', content)
        content = re.sub(r'font-size: 7px;([^"]*margin: 0;">\d)', r'font-size: 6px;\1', content)
        
        with open(filename, 'w') as f:
            f.write(content)

print("Fixed padding on all slides")
