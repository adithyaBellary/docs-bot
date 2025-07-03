from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.client import answer_question
from app.ingest import ingest_documentation

doc_server = FastAPI()

class QueryRequest(BaseModel):
  query: str

fe_path = "docs-bot-frontend/dist"

@doc_server.post("/ask")
def ask(request: QueryRequest):
  answer = answer_question(request.query)
  return {"answer": answer}

@doc_server.post("/ingest")
async def ingest(request: Request):
  data = await request.json()
  url = data["url"]
  ingest_documentation(url)
  print('ingested:', url)
  return {"message": f"ingested: {url}"}


messages_archive = []
@doc_server.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  while True:
      data = await websocket.receive_text()
      messages_archive.append({
        "role": "user",
        "content": data
      })

      answer = answer_question(data, messages_archive)
      messages_archive.append({
        "role": "assistant",
        "content": answer
      })
      await websocket.send_text(answer)

doc_server.mount("/", StaticFiles(directory=fe_path, html=True), name="docs-bot-frontend")
