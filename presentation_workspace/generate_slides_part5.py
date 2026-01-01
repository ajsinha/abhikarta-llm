import os

def create_slide(slide_num, title, content_html):
    return f'''<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="professional-theme.css"></head>
<body class="col" style="width: 960px; height: 540px; background: #F4F9FD;">
  <div style="background: #0079C1; padding: 12px 40px; display: flex; justify-content: space-between; align-items: center;">
    <p style="font-size: 18px; color: #FFFFFF; margin: 0; font-weight: 600;">{title}</p>
    <p style="font-size: 11px; color: #FFFFFF; margin: 0;">Abhikarta-LLM v1.4.7</p>
  </div>
  
  <div class="fill-height" style="background: #F4F9FD; padding: 16px 40px;">
{content_html}
  </div>
  
  <div style="background: #0079C1; padding: 8px 40px; display: flex; justify-content: space-between; align-items: center;">
    <p style="font-size: 9px; color: #FFFFFF; margin: 0;">Copyright © 2025-2030 Ashutosh Sinha | Patent Pending</p>
    <p style="font-size: 9px; color: #FFFFFF; margin: 0;">{slide_num}</p>
  </div>
</body>
</html>'''

slides = []

# Slide 48: Open Source Acknowledgements Part 3
slides.append((48, "Open Source: Utilities & Tools", '''
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Click</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">BSD License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">CLI framework</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Rich</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Terminal formatting</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">PyYAML</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">YAML parser</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Requests</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Apache 2.0</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">HTTP library</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">aiohttp</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">Apache 2.0</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Async HTTP client</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">NumPy</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">BSD License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Numerical computing</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">Pandas</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">BSD License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Data analysis</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">PyPDF</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">BSD License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">PDF processing</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 12px; border-left: 4px solid #0079C1;">
        <p style="font-size: 12px; color: #0079C1; margin: 0; font-weight: 600;">python-docx</p>
        <p style="font-size: 10px; color: #5A7A9C; margin: 6px 0 0 0;">MIT License</p>
        <p style="font-size: 9px; color: #5A7A9C; margin: 4px 0 0 0;">Word document processing</p>
      </div>
    </div>'''))

# Slide 49: Licensing & IP
slides.append((49, "Licensing & Intellectual Property", '''
    <div style="display: flex; gap: 20px; height: 100%;">
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #ED1C24;">
          <p style="font-size: 14px; color: #ED1C24; margin: 0; font-weight: 600;">Proprietary License</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.5;">Abhikarta-LLM is proprietary software. All rights reserved. Unauthorized copying, modification, distribution, or use is strictly prohibited.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
          <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Patent Pending</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.5;">AI Organization Management technology and hierarchical AI governance framework are patent pending innovations.</p>
        </div>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 14px; color: #1A3A5C; margin: 0; font-weight: 600;">Copyright</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.5;">Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.</p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px;">
          <p style="font-size: 14px; color: #1A3A5C; margin: 0; font-weight: 600;">Open Source Dependencies</p>
          <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.5;">This software incorporates open source components under their respective licenses as documented in the acknowledgements section.</p>
        </div>
      </div>
    </div>'''))

# Slide 50: Contact & Resources
slides.append((50, "Contact & Resources", '''
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; height: 100%;">
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Documentation</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.5;">Comprehensive guides, API reference, tutorials available at /docs after installation or in the docs/ folder.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Research Paper</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.5;">Technical whitepaper on architecture, design decisions, and implementation details available in docs/research/.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #ED1C24;">
        <p style="font-size: 14px; color: #ED1C24; margin: 0; font-weight: 600;">Support</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.5;">Enterprise support available. Contact the development team for licensing, customization, and deployment assistance.</p>
      </div>
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 16px; border-left: 4px solid #0079C1;">
        <p style="font-size: 14px; color: #0079C1; margin: 0; font-weight: 600;">Training</p>
        <p style="font-size: 11px; color: #5A7A9C; margin: 10px 0 0 0; line-height: 1.5;">Custom training programs available for development teams, administrators, and business users.</p>
      </div>
    </div>'''))

# Slide 51: Final Slide - Copyright Notice
slides.append((51, "Copyright Notice", '''
    <div class="col center" style="height: 100%;">
      <p style="font-size: 32px; color: #0079C1; margin: 0; font-weight: 700;">Abhikarta-LLM</p>
      <p style="font-size: 16px; color: #1A3A5C; margin: 12px 0 0 0;">Enterprise AI Orchestration Platform</p>
      <p style="font-size: 14px; color: #5A7A9C; margin: 8px 0 0 0;">Version 1.4.7</p>
      
      <div style="background: #FFFFFF; border: 1px solid #D0E4F0; border-radius: 8px; padding: 20px 40px; margin-top: 28px; text-align: center;">
        <p style="font-size: 13px; color: #1A3A5C; margin: 0; font-weight: 600;">Copyright © 2025-2030 Ashutosh Sinha</p>
        <p style="font-size: 12px; color: #5A7A9C; margin: 8px 0 0 0;">All Rights Reserved</p>
        <p style="font-size: 12px; color: #ED1C24; margin: 8px 0 0 0; font-weight: 600;">PATENT PENDING</p>
      </div>
      
      <p style="font-size: 10px; color: #5A7A9C; margin-top: 20px; text-align: center; line-height: 1.5;">This presentation and all contents are confidential and proprietary.<br/>Unauthorized reproduction or distribution is prohibited.</p>
    </div>'''))

for num, title, content in slides:
    filename = f"slide{num:02d}.html"
    with open(filename, 'w') as f:
        f.write(create_slide(num, title, content))
    print(f"Created {filename}")

print("Part 5 slides created - Total 51 slides")
