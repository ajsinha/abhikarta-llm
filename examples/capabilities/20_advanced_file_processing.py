"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.5

Example 20: Advanced File Processing
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.file_processors import (
    CSVProcessor, JSONProcessor, ProcessedFile
)

def main():
    print("=" * 70 + "\nEXAMPLE 20: ADVANCED FILE PROCESSING\n" + "=" * 70)
    
    print("\n1. CSV to Markdown Table:")
    print("   markdown = CSVProcessor.to_markdown_table('data.csv')")
    print("   # Creates beautiful markdown tables")
    
    print("\n2. Extract structured data:")
    print("   result = CSVProcessor.read_csv('sales.csv')")
    print("   data = result.structured_data  # List of dicts")
    print("   # Process data programmatically")
    
    print("\n3. JSON with metadata:")
    print("   result = JSONProcessor.read_json('config.json')")
    print("   print(f'Keys: {result.metadata[\"type\"]}')")
    print("   data = result.structured_data")
    
    print("\n4. ProcessedFile attributes:")
    print("   - content: Extracted text")
    print("   - metadata: File info (pages, rows, etc.)")
    print("   - file_type: Type (pdf, csv, etc.)")
    print("   - structured_data: Original data structure")
    
    print("\n5. Smart file handling:")
    print("   from llm.abstraction.file_processors import UniversalFileProcessor")
    print("   processor = UniversalFileProcessor()")
    print("   ")
    print("   # Automatically handles any file type")
    print("   result = processor.process('unknown_file.xyz')")
    print("   # Falls back to text reading")
    
    print("\n6. Batch processing with error handling:")
    print("   files = ['file1.pdf', 'missing.csv', 'file3.json']")
    print("   results = processor.batch_process(files)")
    print("   ")
    print("   for result in results:")
    print("       if 'error' in result.metadata:")
    print("           print(f'Error: {result.metadata[\"error\"]}')")
    print("       else:")
    print("           print(result.content)")
    
    print("\n✅ Example completed!")
    print("\n💡 Transparent file processing for AI applications")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.5"""
