"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 17: Multimodal - Audio
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.multimodal import MultimodalHandler

def main():
    print("=" * 70 + "\nEXAMPLE 17: MULTIMODAL - AUDIO\n" + "=" * 70)
    
    handler = MultimodalHandler()
    
    print("\n🎵 Multimodal Support - Audio Handling")
    print("\nSupported audio formats:")
    for ext in sorted(handler.SUPPORTED_AUDIO):
        print(f"  ✅ {ext}")
    
    print("\n💡 Usage Example:")
    print("""
    handler = MultimodalHandler()
    
    # Load audio file
    audio = handler.load_audio('speech.mp3')
    
    # Transcribe with Whisper (OpenAI)
    facade = UnifiedLLMFacade(config)
    response = facade.transcribe(audio)
    print(response.text)
    
    # Or use with multimodal models
    response = facade.complete(
        "Transcribe this audio",
        media=[audio]
    )
    """)
    
    print("\n✅ Example completed!")
    print("\n💡 Note: Audio support available via:")
    print("   - OpenAI Whisper (transcription)")
    print("   - Google Speech-to-Text")
    print("   - AWS Transcribe")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
