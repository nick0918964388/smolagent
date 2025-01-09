from init_asset import updated_description
from smolagents import CodeAgent, LiteLLMModel, GradioUI
from sqltool import sql_engine_db2
import gradio as gr


sql_engine_db2.description = updated_description

model = LiteLLMModel(
    model_id="ollama/qwen2.5-coder-extra:latest",  # 或使用其他 Ollama 模型如 "ollama/llama2" 
    api_base="http://ollama.webtw.xyz:11434",  # Ollama 預設端口
    api_key="ollama",

)
agent = CodeAgent(
    tools=[sql_engine_db2],
    model=model,
    max_iterations=10,
)

agent.run("各機務段的所有車數量")
