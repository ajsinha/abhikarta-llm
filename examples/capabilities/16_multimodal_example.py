"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.5

Example 16: Multimodal Support - Images, Audio, Video
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.multimodal_support import MultimodalProcessor, MediaType

def main():
    print("=" * 70 + "\nEXAMPLE 16: MULTIMODAL SUPPORT\n" + "=" * 70)
    
    processor = MultimodalProcessor()
    
    print("\n✅ Multimodal Processor Initialized")
    print(f"   Supported image formats: {processor.SUPPORTED_IMAGE_FORMATS}")
    print(f"   Supported audio formats: {processor.SUPPORTED_AUDIO_FORMATS}")
    print(f"   Supported video formats: {processor.SUPPORTED_VIDEO_FORMATS}")
    
    # Example: Load image from bytes
    try:
        # Create a simple test image (1x1 pixel)
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        image = processor.load_image(test_image_data, filename="test.png")
        
        print("\n✅ Image loaded successfully")
        print(f"   Type: {image.media_type.value}")
        print(f"   MIME: {image.mime_type}")
        print(f"   Filename: {image.filename}")
        
        # Create multimodal prompt
        prompt = processor.create_prompt(
            text="What's in this image?",
            media=[image]
        )
        
        print("\n✅ Multimodal prompt created")
        print(f"   Text: {prompt['text']}")
        print(f"   Media items: {len(prompt['media'])}")
    
    except Exception as e:
        print(f"\n⚠️  Demo error (expected in test environment): {e}")
    
    print("\n💡 Usage:")
    print("   # Load from file")
    print("   image = processor.load_image('photo.jpg')")
    print("   audio = processor.load_audio('speech.mp3')")
    print("   video = processor.load_video('clip.mp4')")
    print()
    print("   # Create prompt")
    print("   prompt = processor.create_prompt(")
    print("       text='Describe this',")
    print("       media=[image, audio]")
    print("   )")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.5"""
