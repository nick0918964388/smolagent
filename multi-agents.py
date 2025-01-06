from smolagents import CodeAgent, DuckDuckGoSearchTool, ManagedAgent, LiteLLMModel
import gradio as gr
from gradio import ChatMessage
from utils import stream_from_transformers_agent
import time

model = LiteLLMModel(
    model_id="ollama/qwen2.5-coder-extra:latest",
    api_base="http://ollama.webtw.xyz:11434",
    api_key="ollama",
)

class CustomAgent(CodeAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thought_callback = None
    
    def run(self, prompt: str) -> str:
        try:
            # 記錄開始時間
            start_time = time.time()
            
            # 執行搜尋並獲取回應
            response = super().run(prompt)
            
            # 確保回應是字串類型
            if not isinstance(response, str):
                response = str(response)
            
            # 計算處理時間
            process_time = time.time() - start_time
            response = f"{response}\n\n處理時間: {process_time:.2f} 秒"
            
            return response
            
        except Exception as e:
            return f"發生錯誤: {str(e)}"

web_agent = CustomAgent(
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

def create_interface():
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as interface:
        gr.Markdown("""
        # 🤖 AI 智能助手
        這是一個可以幫助您搜尋網路資訊的 AI 助手。您可以：
        - 詢問任何問題
        - 獲取即時網路資訊
        - 查看 AI 的思考過程
        """)
        
        chatbot = gr.Chatbot(
            height=500,
            show_label=False,
            container=True,
            show_copy_button=True,
            bubble_full_width=False,
        )
        
        with gr.Row():
            input_text = gr.Textbox(
                placeholder="請輸入您的問題...",
                lines=2,
                label="輸入",
                show_label=False,
                scale=8
            )
            submit_btn = gr.Button("送出", variant="primary", scale=1)
            clear_btn = gr.Button("清除", scale=1)

        gr.Examples(
            examples=[
                "請幫我搜尋最新的 AI 技術發展趨勢",
                "什麼是大型語言模型？",
                "請解釋一下 Docker 的基本概念",
            ],
            inputs=input_text,
        )

        state = gr.State([])

        def respond(message, chat_history, state):
            try:
                # 更新對話歷史
                chat_history = chat_history or []
                
                # 使用 agent mode 處理回應
                response = manager_agent.run(message)
                
                # 更新對話歷史
                chat_history.append((message, response))
                state.append((message, response))
                
                return "", chat_history, state
                
            except Exception as e:
                error_msg = f"處理請求時發生錯誤: {str(e)}"
                chat_history.append((message, error_msg))
                state.append((message, error_msg))
                return "", chat_history, state

        def clear_history():
            return [], [], []

        submit_btn.click(
            respond,
            inputs=[input_text, chatbot, state],
            outputs=[input_text, chatbot, state],
        )

        input_text.submit(
            respond,
            inputs=[input_text, chatbot, state],
            outputs=[input_text, chatbot, state],
        )

        clear_btn.click(
            clear_history,
            outputs=[chatbot, state, input_text],
        )

    return interface

def interact_with_agent(prompt, messages):
    messages.append(ChatMessage(role="user", content=prompt))
    yield messages
    for msg in stream_from_transformers_agent(manager_agent, prompt):
        messages.append(msg)
        yield messages
    yield messages


with gr.Blocks() as demo:
    stored_message = gr.State([])
    chatbot = gr.Chatbot(label="Agent",
                         type="messages",
                         avatar_images=(None, "https://em-content.zobj.net/source/twitter/53/robot-face_1f916.png"))
    text_input = gr.Textbox(lines=1, label="Chat Message")
    text_input.submit(lambda s: (s, ""), [text_input], [stored_message, text_input]).then(interact_with_agent, [stored_message, chatbot], [chatbot])

if __name__ == "__main__":
    # interface = create_interface1()
    # interface.queue()
    # interface.launch(
    #     server_name="0.0.0.0",
    #     server_port=7860,
    #     share=True,
    #     debug=True
    # )
    demo.launch()