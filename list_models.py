import google.generativeai as genai
from backend.config import settings

def list_models():
    genai.configure(api_key=settings.gemini_api_key)
    print("Available models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
