"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.5

Example 16: Vision/Image Understanding
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
llm_config_path = '/home/ashutosh/PycharmProjects/abhikarta-llm/config/llm_config.json'

from llm.abstraction.facade import UnifiedLLMFacade
from llm.abstraction.multimodal import ImageInput, MultimodalMessage, VisionCapability

def main():
    print("=" * 70 + "\nEXAMPLE 16: VISION/IMAGE UNDERSTANDING\n" + "=" * 70)
    
    print("\n1. Creating image input from URL:")
    image = ImageInput.from_url("https://example.com/image.jpg")
    print(f"   ✅ Image input created: {image.mime_type}")
    
    print("\n2. Creating multimodal message:")
    msg = MultimodalMessage(
        text="What's in this image?",
        images=[image]
    )
    print(f"   ✅ Message with {len(msg.images)} image(s)")
    
    print("\n3. Example formats:")
    print(f"   - OpenAI format: {len(str(msg.to_openai_format()))} chars")
    print(f"   - Anthropic format: {len(str(msg.to_anthropic_format()))} chars")
    
    print("\n4. Vision capability features:")
    print("   - describe_image() - Describe image content")
    print("   - analyze_multiple_images() - Compare images")
    
    print("\n💡 Usage with facade:")
    print("   config = {'providers': {'openai': {'enabled': True, 'model': 'gpt-4-vision-preview'}}}")
    print("   facade = UnifiedLLMFacade(config)")
    print("   response = VisionCapability.describe_image(facade, 'photo.jpg')")
    
    print("\n✅ Example completed!")
    print("\n💡 Supported providers: OpenAI GPT-4V, Google Gemini, Anthropic Claude 3")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.5"""
