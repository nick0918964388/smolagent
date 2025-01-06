from smolagents import CodeAgent, DuckDuckGoSearchTool, ManagedAgent, LiteLLMModel, GradioUI
import time

model = LiteLLMModel(
    model_id="ollama/qwen2.5-coder-extra:latest",
    api_base="http://ollama.webtw.xyz:11434",
    api_key="ollama",
)


web_agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()], 
    model=model
)

managed_web_agent = ManagedAgent(
    agent=web_agent,
    name="web_search",
    description="Runs web searches for you. Give it your query as an argument."
)

manager_agent = CustomAgent(
    tools=[],
    model=model,
    managed_agents=[managed_web_agent]
)

if __name__ == "__main__":
    # 使用smolagents内置的GradioUI
    ui = GradioUI(
        agent=manager_agent,
        # title="🤖 AI 智能助手",
        # description="这是一个可以帮助您搜索网络信息的 AI 助手。",
        # examples=[
        #     "今天天气怎么样？",
        #     "帮我搜索最新的AI新闻",
        #     "Python如何读取CSV文件？"
        # ],
        # theme="soft"
    ).launch()
    
    