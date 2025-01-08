import sys
import json
from pathlib import Path
from typing import Optional, AsyncGenerator

# 添加父目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from init_db2 import engine, updated_description
from smolagents import CodeAgent, LiteLLMModel
from sqltool import sql_engine_db2

# 初始化 FastAPI
app = FastAPI()

# 設定 SQL 引擎描述
sql_engine_db2.description = updated_description

# 初始化模型
model = LiteLLMModel(
    model_id="ollama/qwen2.5-coder-extra:latest",
    api_base="http://ollama.webtw.xyz:11434",
    api_key="ollama",
)

# 初始化 agent
agent = CodeAgent(
    tools=[sql_engine_db2],
    model=model,
    max_iterations=10,
)

# 定義請求模型
class QueryRequest(BaseModel):
    query: str
    history: Optional[list] = []

async def stream_generator(query: str) -> AsyncGenerator[str, None]:
    try:
        for chunk in agent.run(query, stream=True):
            # 將每個步驟轉換為 JSON 格式
            if hasattr(chunk, 'iteration'):  # 檢查是否為 ActionStep
                # 處理 ActionStep 物件
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
                yield f"data: {json.dumps(step_data)}\n\n"
            else:
                # 處理 AgentText 或其他類型的輸出
                final_data = {
                    "type": "message",
                    "content": str(chunk)
                }
                yield f"data: {json.dumps(final_data)}\n\n"
    except Exception as e:
        error_data = {
            "type": "error",
            "error": str(e)
        }
        yield f"data: {json.dumps(error_data)}\n\n"

@app.post("/query/stream")
async def stream_query(request: QueryRequest):
    return StreamingResponse(
        stream_generator(request.query),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )

# 保留原有的非流式 endpoint
@app.post("/query")
async def process_query(request: QueryRequest):
    try:
        response = agent.run(request.query, stream=False  )

        return {"response": response ,"logs":agent.logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康檢查 endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

