"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.5

Example 17: Voice/Audio Processing
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.multimodal import AudioInput, VoiceCapability

def main():
    print("=" * 70 + "\nEXAMPLE 17: VOICE/AUDIO PROCESSING\n" + "=" * 70)
    
    print("\n1. Audio input types:")
    print("   - AudioInput.from_file('audio.wav')")
    print("   - AudioInput.from_bytes(audio_bytes)")
    
    print("\n2. Supported formats:")
    print("   - WAV, MP3, M4A, OGG, FLAC")
    
    print("\n3. Voice capabilities:")
    print("   - transcribe_audio() - Speech to text")
    print("   - text_to_speech() - Text to speech")
    
    print("\n💡 Usage examples:")
    print("\n   # Transcription")
    print("   audio = AudioInput.from_file('recording.mp3')")
    print("   text = VoiceCapability.transcribe_audio(facade, audio)")
    
    print("\n   # Text-to-Speech")
    print("   audio_bytes = VoiceCapability.text_to_speech(")
    print("       facade, 'Hello world', voice='alloy'")
    print("   )")
    
    print("\n✅ Example completed!")
    print("\n💡 Supported providers: OpenAI Whisper, Google STT/TTS")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.5"""
