from init import engine,updated_description
from smolagents import CodeAgent, LiteLLMModel, GradioUI
from sqltool import sql_engine
import gradio as gr

class CustomGradioUI(GradioUI):
    def launch(self, **kwargs):
        with gr.Blocks() as demo:
            stored_message = gr.State([])
            chatbot = gr.Chatbot(
                label="Agent",
                type="messages",
                avatar_images=(
                    None,
                    "https://em-content.zobj.net/source/twitter/53/robot-face_1f916.png",
                ),
            )
            text_input = gr.Textbox(lines=1, label="Chat Message")
            text_input.submit(
                lambda s: (s, ""), [text_input], [stored_message, text_input]
            ).then(self.interact_with_agent, [stored_message, chatbot], [chatbot])

        demo.launch(
            server_name="0.0.0.0",  # 允許外部訪問
            share=True,             # 啟用分享功能
            **kwargs
        )

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
CustomGradioUI(agent).launch()
