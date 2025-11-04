"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 20: Document Q&A
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.document_parser import DocumentParser
from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 20: DOCUMENT Q&A\n" + "=" * 70)
    
    print("\n📚 Document Q&A System")
    print("\n💡 Workflow:")
    print("""
    # 1. Parse document
    parser = DocumentParser()
    doc = parser.parse('contract.pdf')
    
    # 2. Setup LLM
    config = {'providers': {'mock': {'enabled': True}}}
    facade = UnifiedLLMFacade(config)
    
    # 3. Ask questions
    context = f"Document: {doc.text}"
    
    questions = [
        "What is the main topic?",
        "What are the key points?",
        "Summarize in 3 sentences"
    ]
    
    for q in questions:
        response = facade.complete(f"{context}\\n\\nQuestion: {q}")
        print(f"Q: {q}")
        print(f"A: {response.text}\\n")
    """)
    
    # Demo with mock
    config = {'providers': {'mock': {'enabled': True}}}
    facade = UnifiedLLMFacade(config)
    
    mock_doc = "This is a sample document about AI technology."
    question = "What is this document about?"
    
    response = facade.complete(f"Document: {mock_doc}\n\nQuestion: {question}")
    
    print(f"\n📝 Demo:")
    print(f"Document: {mock_doc}")
    print(f"Question: {question}")
    print(f"Answer: {response.text[:100]}...")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
