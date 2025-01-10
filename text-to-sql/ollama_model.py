import ollama
from typing import Optional, AsyncGenerator, Union, Any, Dict
from config import OLLAMA_API_BASE, OLLAMA_MODEL_NAME

class OllamaModel:
    def __init__(self, model_name=None):
        self.model_name = model_name or OLLAMA_MODEL_NAME
        self.client = ollama.Client(host=OLLAMA_API_BASE)
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        try:
            async for response in self.client.generate(
                model=self.model_name,
                prompt=prompt,
                stream=True
            ):
                yield response.response
        except Exception as e:
            print(f"Ollama 生成錯誤: {str(e)}")
            raise e

    async def generate_complete(self, prompt: str) -> str:
        try:
            response = await self.client.generate(
                model=self.model_name,
                prompt=prompt
            )
            return response.response
        except Exception as e:
            print(f"Ollama 生成錯誤: {str(e)}")
            raise e
    
    async def generate(self, prompt: str, stream: bool = False) -> Union[AsyncGenerator[str, None], str]:
        if stream:
            return self.generate_stream(prompt)
        else:
            return await self.generate_complete(prompt)
    
    async def chat_completion_stream(self, messages) -> AsyncGenerator[Dict, None]:
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        async for chunk in self.generate_stream(prompt):
            yield {
                "choices": [{
                    "delta": {"content": chunk},
                    "finish_reason": None
                }]
            }

    async def chat_completion_complete(self, messages) -> Dict:
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        response = await self.generate_complete(prompt)
        return {
            "choices": [{
                "message": {"content": response},
                "finish_reason": "stop"
            }]
        }
    
    # 實現與 LiteLLM 相容的介面
    async def chat_completion(self, messages, stream=False):
        if stream:
            return self.chat_completion_stream(messages)
        else:
            return await self.chat_completion_complete(messages) 