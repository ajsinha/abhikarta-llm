import os
import re

for i in range(1, 52):
    filename = f"slide{i:02d}.html"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            content = f.read()
        
        # Add padding to body
        content = content.replace(
            'style="width: 960px; height: 540px; background: #F4F9FD;"',
            'style="width: 960px; height: 540px; background: #F4F9FD; padding: 0; box-sizing: border-box;"'
        )
        
        # Make sure top bar has proper margin/padding
        content = re.sub(
            r'<div class="fit" style="background: #0079C1; padding: 8px 40px;',
            '<div class="fit" style="background: #0079C1; padding: 6px 40px; margin: 0;',
            content
        )
        
        # Bottom bar
        content = re.sub(
            r'<div class="fit" style="background: #0079C1; padding: 6px 40px; display: flex;',
            '<div class="fit" style="background: #0079C1; padding: 4px 40px; margin: 0; display: flex;',
            content
        )
        
        # Reduce font size in header/footer
        content = re.sub(r'font-size: 10px;([^"]*margin: 0;">Enterprise)', r'font-size: 9px;\1', content)
        content = re.sub(r'font-size: 8px;([^"]*margin: 0;">Copyright)', r'font-size: 7px;\1', content)
        content = re.sub(r'font-size: 8px;([^"]*margin: 0;">Confidential)', r'font-size: 7px;\1', content)
        content = re.sub(r'font-size: 8px;([^"]*margin: 0;">\d)', r'font-size: 7px;\1', content)
        
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"Final fix {filename}")

print("\nAll slides final fixed!")
