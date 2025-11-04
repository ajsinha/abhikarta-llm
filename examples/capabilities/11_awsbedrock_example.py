"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | Email: ajsinha@gmail.com | Version: 3.1.3

Example 11: AWS Bedrock Provider
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm.abstraction.facade import UnifiedLLMFacade

def main():
    print("=" * 70 + "\nEXAMPLE 11: AWS BEDROCK\n" + "=" * 70)
    
    # AWS Bedrock configuration
    config = {
        'providers': {
            'awsbedrock': {
                'enabled': True,
                'region': 'us-east-1',
                'model': 'anthropic.claude-v2',
                # AWS credentials from environment or IAM role
                # aws_access_key_id and aws_secret_access_key optional
            }
        }
    }
    
    try:
        facade = UnifiedLLMFacade(config)
        response = facade.complete("What are the benefits of AWS Bedrock?")
        print(f"\nResponse: {response.text[:200]}...")
        print(f"\nModel: {response.model}")
        print("\n✅ Example completed!")
        print("\n💡 Note: Requires AWS credentials and Bedrock access")
    except Exception as e:
        print(f"\n⚠️  AWS Bedrock not configured: {e}")
        print("\n💡 To use AWS Bedrock:")
        print("   1. Set up AWS credentials")
        print("   2. Enable Bedrock in your AWS account")
        print("   3. Set region and model in config")

if __name__ == "__main__":
    main()

"""Copyright 2025-2030 all rights reserved | Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.3"""
