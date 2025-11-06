"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.6

Example 16: Multimodal - Images
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.multimodal import MultimodalHandler, MediaType

def main():
    print("=" * 70 + "\nEXAMPLE 16: MULTIMODAL - IMAGES\n" + "=" * 70)
    
    handler = MultimodalHandler()
    
    print("\n📸 Multimodal Support - Image Handling")
    print("\nSupported image formats:")
    for ext in sorted(handler.SUPPORTED_IMAGES):
        print(f"  ✅ {ext}")
    
    print("\n💡 Usage Example:")
    print("""
    handler = MultimodalHandler()
    
    # Load from file
    image = handler.load_image('photo.jpg')
    print(f"Type: {image.media_type}")
    print(f"MIME: {image.mime_type}")
    print(f"Data: {image.data[:50]}...")  # Base64
    
    # Load from bytes
    with open('photo.jpg', 'rb') as f:
        image_bytes = f.read()
    image = handler.load_image(image_bytes, mime_type='image/jpeg')
    
    # Use with LLM (providers like GPT-4V, Claude 3, Gemini)
    facade = UnifiedLLMFacade(config)
    response = facade.complete(
        "Describe this image",
        media=[image]
    )
    """)
    
    print("\n✅ Example completed!")
    print("\n💡 Note: Multimodal requires providers like:")
    print("   - OpenAI GPT-4 Vision")
    print("   - Anthropic Claude 3")
    print("   - Google Gemini")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6"""
