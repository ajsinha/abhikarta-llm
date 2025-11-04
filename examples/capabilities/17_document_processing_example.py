"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.5

Example 17: Document Processing - PDF, DOCX, XLSX, etc.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.document_processing import DocumentProcessor, DocumentType

def main():
    print("=" * 70 + "\nEXAMPLE 17: DOCUMENT PROCESSING\n" + "=" * 70)
    
    processor = DocumentProcessor()
    
    print("\n✅ Document Processor Initialized")
    print(f"   Supported formats: {len(processor.get_supported_formats())} types")
    print(f"   Formats: {', '.join(processor.get_supported_formats())}")
    
    # Example: Process text file
    try:
        # Create a test text file
        test_file = "/tmp/test_doc.txt"
        with open(test_file, 'w') as f:
            f.write("This is a test document.\n")
            f.write("It has multiple lines.\n")
            f.write("Testing document processing.")
        
        # Process the document
        content = processor.process(test_file)
        
        print("\n✅ Document processed successfully")
        print(f"   Type: {content.doc_type.value}")
        print(f"   Length: {len(content.text)} characters")
        print(f"   Metadata: {content.metadata}")
        print(f"\n   Content preview:")
        print(f"   {content.text[:100]}...")
        
        # Clean up
        os.remove(test_file)
    
    except Exception as e:
        print(f"\n⚠️  Demo error: {e}")
    
    print("\n💡 Usage:")
    print("   # Process PDF")
    print("   content = processor.process('document.pdf')")
    print()
    print("   # Process DOCX with tables")
    print("   content = processor.process(")
    print("       'report.docx',")
    print("       extract_tables=True")
    print("   )")
    print()
    print("   # Process XLSX")
    print("   content = processor.process('spreadsheet.xlsx')")
    print()
    print("   # Batch process directory")
    print("   from llm.abstraction.document_processing import batch_process_documents")
    print("   results = batch_process_documents('docs/', '*.pdf')")
    
    print("\n💡 Supported formats:")
    print("   • PDF, DOCX, XLSX, PPTX")
    print("   • TXT, MD, HTML, CSV, JSON")
    print("   • And more!")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.5"""
