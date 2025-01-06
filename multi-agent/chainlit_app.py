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
)

web_agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

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
    await cl.Message(content="您好！我是一個可以幫助您搜尋網路資訊的AI助手。請問有什麼我可以幫您的嗎？").send()

@cl.on_message
async def main(message: cl.Message):
    # 顯示思考中的訊息
    msg = cl.Message(content="", disable_feedback=True)
    await msg.send()
    
    # 開始串流回應
    async for chunk in cl.make_async(manager_agent.run)(message.content):
        await msg.stream_token(chunk)
    
    # 完成串流
    await msg.update()

if __name__ == "__main__":
    cl.run() 