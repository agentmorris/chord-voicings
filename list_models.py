import google.generativeai as genai

API_KEY_PATH = r"g:\temp\gemini_key.txt"
with open(API_KEY_PATH, 'r') as f:
    key = f.read().strip()

genai.configure(api_key=key)
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
