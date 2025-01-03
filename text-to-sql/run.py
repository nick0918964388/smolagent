from init import engine,updated_description
from smolagents import CodeAgent, HfApiModel
from sqltool import sql_engine

sql_engine.description = updated_description

agent = CodeAgent(
    tools=[sql_engine],
    model=HfApiModel("Qwen/Qwen2.5-Coder-32B-Instruct"),
)
# agent.run("Can you give me the name of the client who got the most expensive receipt?")
# agent.run("Alex Mason's total price?")
agent.run("Which receipt got more total money from price and tip?")