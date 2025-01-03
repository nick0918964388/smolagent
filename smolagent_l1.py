from smolagents import CodeAgent,ToolCallingAgent, HfApiModel, PythonInterpreterTool
from huggingface_hub import login
from config import HF_API_KEY

login(HF_API_KEY)

model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"

model = HfApiModel(model_id=model_id)
agent = CodeAgent(tools=[], model=model, add_base_tools=True)
# agent = ToolCallingAgent(tools=[PythonInterpreterTool()], model=model)

agent.run(
    "Could you give me the 118th number in the Fibonacci sequence?",
)
# agent.run(
#     "sum 1~100"
# )

