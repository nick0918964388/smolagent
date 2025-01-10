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
from config import HF_API_KEY,DEEPSEEK_API_KEY
# 修改導入路徑

if HF_API_KEY:
    login(HF_API_KEY)

# 初始化 FastAPI
app = FastAPI()

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
        response = manager_agent.run(request.query, stream=False  )

        return {"response": response ,"logs":asset_agent.logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康檢查 endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

