"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.5

Example 18: Voice / Audio Processing
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from llm.abstraction.multimodal import VoiceProcessor
from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 18: VOICE / AUDIO PROCESSING\n" + "=" * 70)
    
    processor = VoiceProcessor()
    
    print("\n🎤 Voice Capabilities:")
    print("  ✅ Audio transcription")
    print("  ✅ Audio summarization")
    print("  ✅ Key points extraction")
    print("  ✅ Translation")
    print("  ✅ Sentiment analysis")
    
    print("\n💡 Usage Examples:")
    print("""
    # Transcribe audio
    processor = VoiceProcessor()
    
    text = processor.transcribe("recording.mp3")
    
    # Summarize audio content
    summary = processor.summarize_audio(
        "meeting.mp3",
        facade
    )
    
    # Extract key points from audio
    points = processor.extract_key_points_from_audio(
        "presentation.mp3",
        facade,
        num_points=5
    )
    
    # Transcribe and translate
    result = processor.transcribe_and_translate(
        "spanish_audio.mp3",
        facade,
        target_language="English"
    )
    
    # Analyze sentiment
    sentiment = processor.analyze_sentiment(
        "customer_call.mp3",
        facade
    )
    """)
    
    print("\n✅ Voice processing capabilities available!")
    print("\n💡 Transcription providers:")
    print("   - OpenAI Whisper API")
    print("   - Local Whisper model")
    print("\n💡 Install dependencies:")
    print("   pip install openai  # For OpenAI Whisper")
    print("   pip install openai-whisper  # For local Whisper")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.5"""
