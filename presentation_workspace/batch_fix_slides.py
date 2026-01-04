import os
import re

def fix_slide(content):
    # Replace the body and div structure with properly sized elements using fit class
    # The issue is that the top and bottom bars need "fit" class to not expand
    
    # Pattern to find the content between the header and footer divs
    # We need to add "fit" class to the header and footer divs
    
    # Fix: Add fit class to top bar
    content = re.sub(
        r'<div style="background: #0079C1; padding: 12px 40px;',
        '<div class="fit" style="background: #0079C1; padding: 8px 40px;',
        content
    )
    content = re.sub(
        r'<div style="background: #0079C1; padding: 10px 40px;',
        '<div class="fit" style="background: #0079C1; padding: 8px 40px;',
        content
    )
    
    # Fix: Add fit class to bottom bar
    content = re.sub(
        r'<div style="background: #0079C1; padding: 8px 40px; display: flex;',
        '<div class="fit" style="background: #0079C1; padding: 6px 40px; display: flex;',
        content
    )
    content = re.sub(
        r'<div style="background: #0079C1; padding: 6px 40px; display: flex;',
        '<div class="fit" style="background: #0079C1; padding: 6px 40px; display: flex;',
        content
    )
    
    # Reduce font sizes slightly
    content = re.sub(r'font-size: 18px;([^"]*color: #FFFFFF)', r'font-size: 14px;\1', content)
    content = re.sub(r'font-size: 11px;([^"]*color: #FFFFFF[^"]*margin: 0;">Abhikarta)', r'font-size: 9px;\1', content)
    
    # Reduce content area padding
    content = re.sub(r'padding: 16px 40px;', r'padding: 12px 40px;', content)
    content = re.sub(r'padding: 20px 40px;', r'padding: 12px 40px;', content)
    
    # Footer text size
    content = re.sub(r'font-size: 9px;([^"]*color: #FFFFFF[^"]*margin: 0;">Copyright)', r'font-size: 8px;\1', content)
    content = re.sub(r'font-size: 9px;([^"]*color: #FFFFFF[^"]*margin: 0;">\d)', r'font-size: 8px;\1', content)
    
    return content

# Process all slides
for i in range(1, 52):
    filename = f"slide{i:02d}.html"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            content = f.read()
        
        fixed_content = fix_slide(content)
        
        with open(filename, 'w') as f:
            f.write(fixed_content)
        
        print(f"Fixed {filename}")

print("\nAll slides fixed!")
