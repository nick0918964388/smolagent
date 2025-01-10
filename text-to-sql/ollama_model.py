import ollama
from typing import Optional, AsyncGenerator, Union
from config import OLLAMA_API_BASE, OLLAMA_MODEL_NAME

class OllamaModel:
    def __init__(self, model_name=None):
        self.model_name = model_name or OLLAMA_MODEL_NAME
        self.client = ollama.Client(host=OLLAMA_API_BASE)
    
    async def generate(self, prompt: str, stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        try:
            if stream:
                async for response in self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    stream=True
                ):
                    yield response.response
            else:
                response = await self.client.generate(
                    model=self.model_name,
                    prompt=prompt
                )
                return response.response
        except Exception as e:
            print(f"Ollama 生成錯誤: {str(e)}")
            raise e
    
    # 實現與 LiteLLM 相容的介面
    async def chat_completion(self, messages, stream=False):
        # 將 messages 轉換為單一 prompt
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        if stream:
            async for chunk in self.generate(prompt, stream=True):
                yield {
                    "choices": [{
                        "delta": {"content": chunk},
                        "finish_reason": None
                    }]
                }
        else:
            response = await self.generate(prompt, stream=False)
            return {
                "choices": [{
                    "message": {"content": response},
                    "finish_reason": "stop"
                }]
            } 