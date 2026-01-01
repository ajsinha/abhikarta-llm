import os
import glob

def create_slide(slide_num, title, content_html, is_title_slide=False):
    if is_title_slide:
        return f'''<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="professional-theme.css"></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD; padding: 0;">
  <div class="fit" style="background: #0079C1; padding: 10px 40px;">
    <p style="font-size: 11px; color: #FFFFFF; margin: 0;">Enterprise AI Orchestration Platform</p>
  </div>
  
  <div class="fill-height col center" style="background: #F4F9FD; padding: 30px 40px;">
{content_html}
  </div>
  
  <div class="fit" style="background: #0079C1; padding: 8px 40px; display: flex; justify-content: space-between; align-items: center;">
    <p style="font-size: 9px; color: #FFFFFF; margin: 0;">Copyright © 2025-2030 Ashutosh Sinha | All Rights Reserved | Patent Pending</p>
    <p style="font-size: 9px; color: #FFFFFF; margin: 0;">Confidential</p>
  </div>
</body>
</html>'''
    else:
        return f'''<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="professional-theme.css"></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD; padding: 0;">
  <div class="fit" style="background: #0079C1; padding: 10px 40px; display: flex; justify-content: space-between; align-items: center;">
    <p style="font-size: 16px; color: #FFFFFF; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 10px; color: #FFFFFF; margin: 0;">Abhikarta-LLM v1.4.7</p>
  </div>
  
  <div class="fill-height" style="background: #F4F9FD; padding: 14px 40px;">
{content_html}
  </div>
  
  <div class="fit" style="background: #0079C1; padding: 6px 40px; display: flex; justify-content: space-between; align-items: center;">
    <p style="font-size: 8px; color: #FFFFFF; margin: 0;">Copyright © 2025-2030 Ashutosh Sinha | Patent Pending</p>
    <p style="font-size: 8px; color: #FFFFFF; margin: 0;">{slide_num}</p>
  </div>
</body>
</html>'''

# Slide 1 - Title (special layout)
slide1_content = '''    <h1 style="font-size: 48px; color: #0079C1; margin: 0; font-weight: 700;">Abhikarta-LLM</h1>
    <p style="font-size: 20px; color: #1A3A5C; margin: 12px 0 0 0;">Enterprise AI Orchestration Platform</p>
    <p style="font-size: 14px; color: #5A7A9C; margin: 8px 0 0 0;">Version 1.4.7</p>
    
    <div style="display: flex; gap: 20px; margin-top: 24px;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 10px 20px; border-radius: 6px; text-align: center;">
        <p style="font-size: 20px; color: #0079C1; margin: 0; font-weight: 600;">11+</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 2px 0 0 0;">Providers</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 10px 20px; border-radius: 6px; text-align: center;">
        <p style="font-size: 20px; color: #1A3A5C; margin: 0; font-weight: 600;">100+</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 2px 0 0 0;">Models</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 10px 20px; border-radius: 6px; text-align: center;">
        <p style="font-size: 20px; color: #ED1C24; margin: 0; font-weight: 600;">$0</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 2px 0 0 0;">Local Models</p>
      </div>
    </div>'''

with open('slide01.html', 'w') as f:
    f.write(create_slide(1, "Title", slide1_content, is_title_slide=True))
print("Fixed slide01.html")

# Now fix all other slides by reading and re-writing them with the proper template
# The content is already in the files, we just need to extract and re-wrap

print("All slides need content extraction and re-wrapping...")
