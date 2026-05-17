import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

def query_ollama(model: str, prompt: str, system: str = "") -> str:
    """Helper function to interact with local Ollama instance."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        # Return fallback or re-raise depending on architecture
        return f"Error: Unable to reach local Ollama model '{model}'."

def extract_excel_data_via_llm(csv_content: str) -> str:
    """
    Milestone 4: Parses arbitrary CSV content to identify tenant info.
    Expects a Qwen2.5 or Llama-3 model.
    """
    system_prompt = "You are a data extraction assistant. Parse the provided CSV and return a structured JSON mapping of tenant details, rent, and deposit."
    prompt = f"Extract details from this CSV:\n{csv_content}"
    return query_ollama(model="qwen2.5:latest", prompt=prompt, system=system_prompt)

def analyze_damage_vision_diff(check_in_photo_base64: str, check_out_photo_base64: str) -> str:
    """
    Milestone 5: Analyzes differences between check-in and check-out photos.
    Expects a Vision model like Qwen-VL or LLaVA.
    Currently, Ollama /api/generate accepts 'images' array for vision models.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": "llava:latest",  # Or your preferred vision model
        "prompt": "Compare these two images of a PG room item. The first is check-in, the second is check-out. Identify any new damage such as scratches, stains, or breakages.",
        "images": [check_in_photo_base64, check_out_photo_base64],
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama Vision Model: {e}")
        return "Error: Unable to analyze images via Ollama."
