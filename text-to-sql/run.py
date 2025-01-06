from init import engine,updated_description
from smolagents import CodeAgent, LiteLLMModel ,GradioUI
from sqltool import sql_engine

sql_engine.description = updated_description

model = LiteLLMModel(
    model_id="ollama/qwen2.5-coder-extra:latest",  # 或使用其他 Ollama 模型如 "ollama/llama2" 
    api_base="http://ollama.webtw.xyz:11434",  # Ollama 預設端口
    api_key="ollama",

)
agent = CodeAgent(
    tools=[sql_engine],
    model=model,
    max_iterations=10,
)
# agent.run("Can you give me the name of the client who got the most expensive receipt?")
# agent.run("Alex Mason's total price?")
# agent.run("Which receipt got more total money from price and tip?")
# agent.run("請給我新竹機務段所有資產 , 新竹機務段是部門名稱 , 請用繁體中文回覆")
GradioUI(agent).launch()
