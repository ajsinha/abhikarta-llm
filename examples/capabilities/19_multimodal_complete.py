"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 19: Complete Multimodal Workflow
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.multimodal import MultimodalHandler
from llm.abstraction.document_parser import DocumentParser

def main():
    print("=" * 70 + "\nEXAMPLE 19: COMPLETE MULTIMODAL WORKFLOW\n" + "=" * 70)
    
    print("\n🎯 Complete Multimodal Pipeline")
    
    print("\n1️⃣ Initialize Handlers")
    print("""
    multimodal = MultimodalHandler()
    parser = DocumentParser()
    facade = UnifiedLLMFacade(config)
    """)
    
    print("\n2️⃣ Process Different Media Types")
    print("""
    # Images
    image = multimodal.load_image('chart.png')
    response = facade.complete("Analyze this chart", media=[image])
    
    # Documents
    doc = parser.parse('report.pdf')
    response = facade.complete(f"Summarize: {doc.text}")
    
    # Audio
    audio = multimodal.load_audio('meeting.mp3')
    transcript = facade.transcribe(audio)
    
    # Video
    video = multimodal.load_video('presentation.mp4')
    response = facade.complete("Describe video", media=[video])
    """)
    
    print("\n3️⃣ Combined Analysis")
    print("""
    # Analyze document with images
    doc = parser.parse('report.pdf')
    image = multimodal.load_image('graph.png')
    
    response = facade.complete(
        f"Based on this document: {doc.text[:1000]}
        And this graph, provide insights",
        media=[image]
    )
    """)
    
    print("\n✅ Example completed!")
    print("\n💡 Supported Use Cases:")
    print("   - Document Q&A with images")
    print("   - Audio transcription + analysis")
    print("   - Video content description")
    print("   - Multi-format data extraction")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
