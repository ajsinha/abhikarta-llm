import os
import re

# Read all slide files and fix the padding issues
for i in range(1, 52):
    filename = f"slide{i:02d}.html"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            content = f.read()
        
        # For content slides (not title or section), increase padding
        if 'padding: 20px 30px' in content:
            content = content.replace('padding: 20px 30px', 'padding: 28px 40px')
        
        # Make header/footer text smaller and add more margin
        content = content.replace('margin-bottom: 12px', 'margin-bottom: 8px')
        content = content.replace('margin-top: 10px', 'margin-top: 6px')
        
        # Make copyright smaller
        content = re.sub(r'font-size: 8px;([^"]*Copyright)', r'font-size: 7px;\1', content)
        content = re.sub(r'font-size: 8px;([^"]*margin: 0;">\d)', r'font-size: 7px;\1', content)
        
        with open(filename, 'w') as f:
            f.write(content)

print("Fixed all content slide templates")
