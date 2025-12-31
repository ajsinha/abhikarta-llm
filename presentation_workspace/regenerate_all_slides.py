import os

def slide_template(num, title, content, is_section=False, is_title=False, is_thank_you=False):
    if is_title:
        return f'''<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="professional-theme.css"></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD;">
  <div class="fit" style="background: #0079C1; padding: 8px 40px;">
    <p style="font-size: 10px; color: #FFFFFF; margin: 0;">Enterprise AI Orchestration Platform</p>
  </div>
  <div class="fill-height col center" style="background: #F4F9FD; padding: 20px 40px;">
{content}
  </div>
  <div class="fit" style="background: #0079C1; padding: 6px 40px; display: flex; justify-content: space-between;">
    <p style="font-size: 8px; color: #FFFFFF; margin: 0;">Copyright © 2025-2030 Ashutosh Sinha | All Rights Reserved | Patent Pending</p>
    <p style="font-size: 8px; color: #FFFFFF; margin: 0;">Confidential</p>
  </div>
</body>
</html>'''
    elif is_section:
        return f'''<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="professional-theme.css"></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD;">
  <div class="fit" style="background: #0079C1; padding: 8px 40px; display: flex; justify-content: space-between;">
    <p style="font-size: 14px; color: #FFFFFF; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 9px; color: #FFFFFF; margin: 0;">Abhikarta-LLM v1.4.6</p>
  </div>
  <div class="fill-height col center" style="background: #F4F9FD; padding: 20px 40px;">
{content}
  </div>
  <div class="fit" style="background: #0079C1; padding: 6px 40px; display: flex; justify-content: space-between;">
    <p style="font-size: 8px; color: #FFFFFF; margin: 0;">Copyright © 2025-2030 Ashutosh Sinha | Patent Pending</p>
    <p style="font-size: 8px; color: #FFFFFF; margin: 0;">{num}</p>
  </div>
</body>
</html>'''
    elif is_thank_you:
        return f'''<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="professional-theme.css"></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD;">
  <div class="fit" style="background: #0079C1; padding: 8px 40px; display: flex; justify-content: space-between;">
    <p style="font-size: 14px; color: #FFFFFF; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 9px; color: #FFFFFF; margin: 0;">Abhikarta-LLM v1.4.6</p>
  </div>
  <div class="fill-height col center" style="background: #F4F9FD; padding: 20px 40px;">
{content}
  </div>
  <div class="fit" style="background: #0079C1; padding: 6px 40px; display: flex; justify-content: space-between;">
    <p style="font-size: 8px; color: #FFFFFF; margin: 0;">Copyright © 2025-2030 Ashutosh Sinha | Patent Pending</p>
    <p style="font-size: 8px; color: #FFFFFF; margin: 0;">{num}</p>
  </div>
</body>
</html>'''
    else:
        return f'''<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="professional-theme.css"></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD;">
  <div class="fit" style="background: #0079C1; padding: 8px 40px; display: flex; justify-content: space-between;">
    <p style="font-size: 14px; color: #FFFFFF; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 9px; color: #FFFFFF; margin: 0;">Abhikarta-LLM v1.4.6</p>
  </div>
  <div class="fill-height" style="background: #F4F9FD; padding: 12px 40px;">
{content}
  </div>
  <div class="fit" style="background: #0079C1; padding: 6px 40px; display: flex; justify-content: space-between;">
    <p style="font-size: 8px; color: #FFFFFF; margin: 0;">Copyright © 2025-2030 Ashutosh Sinha | Patent Pending</p>
    <p style="font-size: 8px; color: #FFFFFF; margin: 0;">{num}</p>
  </div>
</body>
</html>'''

# Define all slides with their content
slides_data = [
    # Slide 1 - Title
    (1, "Title", '''    <h1 style="font-size: 44px; color: #0079C1; margin: 0; font-weight: 700;">Abhikarta-LLM</h1>
    <p style="font-size: 18px; color: #1A3A5C; margin: 10px 0 0 0;">Enterprise AI Orchestration Platform</p>
    <p style="font-size: 13px; color: #5A7A9C; margin: 6px 0 0 0;">Version 1.4.6</p>
    <div style="display: flex; gap: 16px; margin-top: 20px;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 8px 16px; border-radius: 6px; text-align: center;">
        <p style="font-size: 18px; color: #0079C1; margin: 0; font-weight: 600;">11+</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Providers</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 8px 16px; border-radius: 6px; text-align: center;">
        <p style="font-size: 18px; color: #1A3A5C; margin: 0; font-weight: 600;">100+</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Models</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; padding: 8px 16px; border-radius: 6px; text-align: center;">
        <p style="font-size: 18px; color: #ED1C24; margin: 0; font-weight: 600;">$0</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Local Models</p>
      </div>
    </div>''', True, False, False),
    
    # Slide 2 - Table of Contents
    (2, "Table of Contents", '''    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; border-left: 3px solid #0079C1;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">1. Executive Summary</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Platform overview and value</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; border-left: 3px solid #0079C1;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">2. Market Challenges</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Problems we solve</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; border-left: 3px solid #0079C1;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">3. Platform Architecture</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">System design</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; border-left: 3px solid #0079C1;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">4. Multi-Provider Support</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">11+ LLM providers</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; border-left: 3px solid #ED1C24;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">5. Agent Framework</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Building AI agents</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; border-left: 3px solid #ED1C24;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">6. Workflow DAG System</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Visual orchestration</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; border-left: 3px solid #ED1C24;">
        <p style="font-size: 11px; color: #ED1C24; margin: 0; font-weight: 600;">7. AI Organizations</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Hierarchical governance</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; border-left: 3px solid #0079C1;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">8. Security & Governance</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Enterprise controls</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; border-left: 3px solid #0079C1;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">9. Use Cases</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Real-world applications</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 6px; padding: 10px; border-left: 3px solid #0079C1;">
        <p style="font-size: 11px; color: #0079C1; margin: 0; font-weight: 600;">10. Appendix</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 2px 0 0 0;">Competition & Acknowledgements</p>
      </div>
    </div>''', False, False, False),
]

# Write first 2 slides
for num, title, content, is_title, is_section, is_thank_you in slides_data:
    filename = f"slide{num:02d}.html"
    with open(filename, 'w') as f:
        f.write(slide_template(num, title, content, is_section, is_title, is_thank_you))
    print(f"Created {filename}")

print("First 2 slides created with fixed template")
