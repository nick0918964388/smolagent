import sys
import json
from pathlib import Path
from typing import Optional, AsyncGenerator
from ollama_model import OllamaModel

# 添加父目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from init_asset import asset_description
from init_carava import carava_description
from smolagents import CodeAgent, LiteLLMModel, ManagedAgent,HfApiModel
from sqltool import sql_engine_db2_asset, sql_engine_db2_carava
from huggingface_hub import login
from config import HF_API_KEY,DEEPSEEK_API_KEY, OLLAMA_MODEL_NAME, OLLAMA_PROMPT_TEMPLATE
from fastapi.middleware.cors import CORSMiddleware
# 修改導入路徑

if HF_API_KEY:
    login(HF_API_KEY)

# 初始化 FastAPI
app = FastAPI()
# 加入 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在正式環境中應該限制允許的來源
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 headers
)

# 設定 SQL 引擎描述
sql_engine_db2_asset.description = asset_description
sql_engine_db2_carava.description = carava_description

# 使用預設模型
# model = OllamaModel()

# 或指定特定模型
# model = OllamaModel(model_name="different-model")

# 或使用 Deepseek
model = LiteLLMModel(model_id="deepseek/deepseek-chat",api_base="https://api.deepseek.com/v1" , api_key=DEEPSEEK_API_KEY)

# 初始化 agent
asset_agent = CodeAgent(
    tools=[sql_engine_db2_asset],
    model=model,
    max_iterations=10
)
managed_asset_agent = ManagedAgent(
    agent=asset_agent,
    name="query_asset",
    description="查詢資產(車輛相關數量)資料",
    additional_prompting = "資料庫的Schema: " + asset_description,
    provide_run_summary = True
)

car_avaliable_agent = CodeAgent(
    tools=[sql_engine_db2_carava],
    model=model,
    max_iterations=10,    
)

managed_car_avaliable_agent = ManagedAgent(
    agent=car_avaliable_agent,
    name="query_car_avaliable",
    description="查詢車輛本日可用率相關 : 如配屬數量、借入數量、現有數量、定期數量、段修數量、待料待修數量、無火迴送數量、停用數量、備註",
    additional_prompting = "資料庫的Schema: " + carava_description,
    provide_run_summary = True
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[managed_asset_agent,managed_car_avaliable_agent],
    additional_authorized_imports=["time", "numpy", "pandas"],
)

# 定義請求模型
class QueryRequest(BaseModel):
    query: str
    history: Optional[list] = []

# 在現有的 QueryRequest 類別後添加新的請求模型
class OllamaRequest(BaseModel):
    question: str
    context: str
    stream: Optional[bool] = True

# 添加新的串流生成器函數
async def ollama_stream_generator(question: str, context: str) -> AsyncGenerator[str, None]:
    try:
        ollama_model = OllamaModel(model_name=OLLAMA_MODEL_NAME)
        yield "data: {\"type\": \"connected\"}\n\n"
        
        # 使用 config 中的 prompt template，同時傳入 question 和 context
        prompt = OLLAMA_PROMPT_TEMPLATE.format(
            question=question,
            context=context
        )
        
        for chunk in ollama_model.stream(prompt):
            chunk_data = {
                "type": "message",
                "content": chunk
            }
            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
            
        yield "data: {\"type\": \"done\"}\n\n"
            
    except Exception as e:
        error_data = {
            "type": "error",
            "error": str(e)
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

# 添加新的 endpoint
@app.post("/summary")
async def process_ollama(request: OllamaRequest):
    try:
        if request.stream:
            return StreamingResponse(
                ollama_stream_generator(request.question, request.context),
                media_type="text/event-stream",
                headers={
                    'Cache-Control': 'no-cache, no-transform',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no',
                    'Content-Type': 'text/event-stream; charset=utf-8',
                    'Access-Control-Allow-Origin': '*',
                }
            )
        else:
            ollama_model = OllamaModel(model_name=OLLAMA_MODEL_NAME)
            prompt = OLLAMA_PROMPT_TEMPLATE.format(
                question=request.question,
                context=request.context
            )
            response = ollama_model.generate(prompt)
            return {"response": response}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def stream_generator(query: str) -> AsyncGenerator[str, None]:
    try:
        # 發送初始連接建立消息
        yield "data: {\"type\": \"connected\"}\n\n"
        
        for chunk in manager_agent.run(query, stream=True):
            if hasattr(chunk, 'iteration'):  # ActionStep
                step_data = {
                    "type": "step",
                    "step_number": chunk.iteration,
                    "duration": chunk.duration,
                    "error": str(chunk.error) if chunk.error else None,
                    "llm_output": chunk.llm_output,
                    "observations": chunk.observations,
                    "action_output": chunk.action_output,
                    "start_time": chunk.start_time,
                    "end_time": chunk.end_time,
                }
                # 確保每條消息以data:開頭，並以兩個換行結束
                yield f"data: {json.dumps(step_data, ensure_ascii=False)}\n\n"
            else:
                final_data = {
                    "type": "message",
                    "content": str(chunk)
                }
                yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
                
        # 發送結束消息
        yield "data: {\"type\": \"done\"}\n\n"
            
    except Exception as e:
        error_data = {
            "type": "error",
            "error": str(e)
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

@app.post("/query/stream")
async def stream_query(request: QueryRequest):
    return StreamingResponse(
        stream_generator(request.query),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',  # 禁用Nginx緩衝
            'Content-Type': 'text/event-stream; charset=utf-8',
            'Access-Control-Allow-Origin': '*',  # 如果需要CORS
        }
    )

# 保留原有的非流式 endpoint
@app.post("/query")
async def process_query(request: QueryRequest):
    try:
        response = manager_agent.run(request.query, stream=False)
        return {"response": response, "logs": asset_agent.logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康檢查 endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

