"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.5

Example 18: File Processing (PDF, DOCX, CSV, JSON, TXT)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.file_processors import (
    UniversalFileProcessor, process_file, process_file_for_prompt,
    PDFProcessor, DOCXProcessor, CSVProcessor, JSONProcessor, TXTProcessor
)

def main():
    print("=" * 70 + "\nEXAMPLE 18: FILE PROCESSING\n" + "=" * 70)
    
    print("\n1. Universal File Processor:")
    processor = UniversalFileProcessor()
    print("   ✅ Supports: PDF, DOCX, CSV, JSON, TXT, MD, LOG")
    
    print("\n2. Usage examples:")
    
    print("\n   # Process any file automatically")
    print("   result = process_file('document.pdf')")
    print("   print(result.content)")
    
    print("\n   # Process for LLM prompt")
    print("   prompt = process_file_for_prompt('data.csv', 'Summarize this data')")
    
    print("\n   # Specific processors")
    print("   pdf_result = PDFProcessor.extract_text('doc.pdf')")
    print("   docx_result = DOCXProcessor.extract_text('doc.docx')")
    print("   csv_result = CSVProcessor.read_csv('data.csv')")
    print("   json_result = JSONProcessor.read_json('config.json')")
    
    print("\n3. With LLM Facade:")
    print("   from llm.abstraction.facade import UnifiedLLMFacade")
    print("   ")
    print("   # Process file and send to LLM")
    print("   file_content = processor.process_for_llm('report.pdf')")
    print("   response = facade.complete(f'Summarize: {file_content}')")
    
    print("\n4. Batch processing:")
    print("   files = ['file1.pdf', 'file2.docx', 'file3.csv']")
    print("   results = processor.batch_process(files)")
    
    print("\n✅ Example completed!")
    print("\n💡 Install optional: pip install PyPDF2 python-docx")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.5"""
