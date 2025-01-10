import requests
import json
from config import OLLAMA_API_BASE

class OllamaModel:
    def __init__(self, model_name="llama2"):
        self.model_name = model_name
        self.api_base = OLLAMA_API_BASE

    def generate(self, prompt: str) -> str:
        """生成完整回應"""
        url = f"{self.api_base}/api/generate"
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()["response"]

    def stream(self, prompt: str):
        """串流生成回應"""
        url = f"{self.api_base}/api/generate"
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True
        }
        
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if "response" in json_response:
                    yield json_response["response"] 