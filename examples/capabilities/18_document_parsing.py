"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 18: Document Parsing
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.document_parser import DocumentParser

def main():
    print("=" * 70 + "\nEXAMPLE 18: DOCUMENT PARSING\n" + "=" * 70)
    
    parser = DocumentParser()
    
    print("\n📄 Document Format Support")
    print("\nSupported formats:")
    for ext, fmt in sorted(parser.SUPPORTED_FORMATS.items()):
        print(f"  ✅ {ext:8s} - {fmt.value}")
    
    print("\n💡 Usage Example:")
    print("""
    from llm.abstraction.document_parser import DocumentParser
    
    parser = DocumentParser()
    
    # Parse PDF
    doc = parser.parse('report.pdf')
    print(doc.text)
    print(f"Pages: {doc.page_count}")
    
    # Parse DOCX
    doc = parser.parse('document.docx')
    print(doc.text)
    
    # Parse Excel
    doc = parser.parse('data.xlsx')
    print(doc.text)
    
    # Use with LLM
    facade = UnifiedLLMFacade(config)
    response = facade.complete(f"Summarize: {doc.text}")
    """)
    
    print("\n✅ Example completed!")
    print("\n💡 Optional dependencies:")
    print("   pip install PyPDF2        # PDF support")
    print("   pip install python-docx   # DOCX support")
    print("   pip install openpyxl      # Excel support")
    print("   pip install beautifulsoup4  # HTML support")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
