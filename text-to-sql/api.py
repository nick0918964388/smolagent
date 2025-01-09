import sys
import json
from pathlib import Path
from typing import Optional, AsyncGenerator

# 添加父目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from init_asset import asset_description
from init_carava import carava_description
from smolagents import CodeAgent, LiteLLMModel , ManagedAgent
from sqltool import sql_engine_db2_asset, sql_engine_db2_carava


# 初始化 FastAPI
app = FastAPI()

# 設定 SQL 引擎描述
sql_engine_db2_asset.description = asset_description
sql_engine_db2_carava.description = carava_description
# sql_engine_db2.description = updated_description

# 初始化模型
# model = LiteLLMModel(
#     model_id="ollama/qwen2.5-coder-extra:latest",
#     api_base="http://ollama.webtw.xyz:11434",
#     api_key="ollama"    
# )
# model = LiteLLMModel(model_id="groq/llama3-70b-8192")
model = LiteLLMModel(model_id="github/llama3-70b-8192")

# 初始化 agent
asset_agent = CodeAgent(
    tools=[sql_engine_db2_asset],
    model=model,
    max_iterations=10
)
managed_asset_agent = ManagedAgent(
    agent=asset_agent,
    name="query_asset",
    description=asset_description + " \n\n 查詢資產(車輛相關數量)資料",
)

car_avaliable_agent = CodeAgent(
    tools=[sql_engine_db2_carava],
    model=model,
    max_iterations=10,    
)

managed_car_avaliable_agent = ManagedAgent(
    agent=car_avaliable_agent,
    name="query_car_avaliable",
    description=carava_description + " \n\n 查詢車輛配屬數量、借入數量、現有數量、定期數量、段修數量、待料待修數量、無火迴送數量、停用數量、備註",
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
        
        for chunk in asset_agent.run(query, stream=True):
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
        response = asset_agent.run(request.query, stream=False  )

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

