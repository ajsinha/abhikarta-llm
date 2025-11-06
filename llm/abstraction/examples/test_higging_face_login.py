from huggingface_hub import login, HfApi
from huggingface_hub import InferenceClient
import os

# Replace with your actual token
YOUR_TOKEN = os.getenv('HUGGINGFACE_API_KEY', 'your-hf-key')

# 1. Test Login/Authentication
login(token=YOUR_TOKEN)
print("Authentication successful.")

# 2. Test Model Access (Checking permissions to download/access model info)
api = HfApi()
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
try:
    api.model_info(model_name)
    print("SUCCESS: Token has access to Llama 3 model information.")
except Exception as e:
    print(f"FAILURE: Could not access model. Error: {e}")
    print("Please ensure you accepted the Llama 3 license on the model page.")

client = InferenceClient(api_key=YOUR_TOKEN) #token=YOUR_TOKEN, a


completion = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
)

print(completion.choices[0].message)

#
#client = InferenceClient(token="hf_your_token_here")
message = "Explain quantum computing in simple terms."
response = client.chat.completions.create(
    messages=[{"role": "user", "content": message}],
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    max_tokens=200,  # Equivalent to max_new_tokens
    temperature=0.7,
    stream=False
)

# Access the generated text
print(response.choices[0].message.content)

# Recommended Llama model ID for general-purpose generation
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"


client = InferenceClient(api_key=YOUR_TOKEN, model=MODEL_ID)
# Use the text_generate method
output = client.text_generation(
    prompt="Write a short, four-line poem about a cat sitting in a sunbeam.",
    max_new_tokens=64,
    temperature=0.8,
)

print(output)