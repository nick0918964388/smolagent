import chainlit as cl
from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    ManagedAgent,
    LiteLLMModel,
)

model = LiteLLMModel(
    model_id="ollama/qwen2.5-coder-extra:latest",
    api_base="http://ollama.webtw.xyz:11434",
    api_key="ollama",
    **{
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 0.9,
        "stop": ["\n\n"]
    }
)

web_agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    temperature=0.7
)

managed_web_agent = ManagedAgent(
    agent=web_agent,
    name="web_search",
    description="Runs web searches for you. Give it your query as an argument."
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[managed_web_agent]
)

@cl.on_chat_start
async def start():
    await cl.Message("您好！我是一個可以幫助您搜尋網路資訊的AI助手。請問有什麼我可以幫您的嗎？").send()

@cl.on_message
async def main(message: cl.Message):
    # 顯示思考中的狀態
    async with cl.Step("思考中..."):
        try:
            # 取得回應
            response = manager_agent.run(message.content)
            
            # 發送回應
            await cl.Message(response).send()
            
        except Exception as e:
            await cl.Message(f"發生錯誤: {str(e)}").send()

if __name__ == "__main__":
    cl.run(host="0.0.0.0", port=8000) 