"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.5

Example 16: Document Processing - PDF, DOCX, CSV, TXT, JSON
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.documents import DocumentProcessor, auto_load
from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 16: DOCUMENT PROCESSING\n" + "=" * 70)
    
    processor = DocumentProcessor()
    
    print("\n📄 Document Loaders:")
    print("  ✅ PDF - load_pdf()")
    print("  ✅ DOCX - load_docx()")
    print("  ✅ CSV - load_csv()")
    print("  ✅ TXT - load_txt()")
    print("  ✅ JSON - load_json()")
    print("  ✅ AUTO - auto_load() (auto-detect type)")
    
    print("\n💡 Usage Examples:")
    print("""
    # Load any document
    from llm.abstraction.documents import auto_load
    content = auto_load("document.pdf")
    
    # With LLM integration
    processor = DocumentProcessor()
    text = processor.load("report.pdf")
    summary = processor.process_with_llm(
        text, 
        facade,
        "Summarize this document"
    )
    
    # Summarize long documents (auto-chunking)
    summary = processor.summarize_long_document(
        "long_report.pdf",
        facade,
        chunk_size=2000
    )
    
    # Extract key points
    points = processor.extract_key_points(
        "document.pdf",
        facade,
        num_points=5
    )
    """)
    
    print("\n✅ Document processing capabilities available!")
    print("\n💡 Install dependencies:")
    print("   pip install PyPDF2 python-docx")
    print("   # or: pip install pdfplumber")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.5"""
