from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    ManagedAgent,
    DuckDuckGoSearchTool,
    LiteLLMModel,
    GradioUI
)
from init import visit_webpage

model = LiteLLMModel(
    model_id="ollama/qwen2.5-coder-extra:latest",  # 或使用其他 Ollama 模型如 "ollama/llama2" 
    api_base="http://ollama.webtw.xyz:11434",  # Ollama 預設端口
    api_key="ollama",
)

web_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), visit_webpage],
    model=model,
    max_iterations=10,
)

managed_web_agent = ManagedAgent(
    agent=web_agent,
    name="search",
    description="Runs web searches for you. Give it your query as an argument.",
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[managed_web_agent],
    additional_authorized_imports=["time", "numpy", "pandas"],
)

#answer = manager_agent.run("If LLM trainings continue to scale up at the current rythm until 2030, what would be the electric power in GW required to power the biggest training runs by 2030? What does that correspond to, compared to some contries? Please provide a source for any number used.")
answer = manager_agent.run("台灣最高的山? Please provide a source for any number used. 請用繁體中文回覆")

# if __name__ == "__main__":
#     ui = GradioUI(
#         manager_agent
#     ).launch()