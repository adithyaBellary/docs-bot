from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.client import answer_question
from app.ingest import ingest_documentation
# import uvicorn

# PORT = 8000
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


@doc_server.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(data)

        # answer = answer_question(data)
        # await websocket.send_text(answer)

doc_server.mount("/chat", StaticFiles(directory=fe_path, html=True), name="docs-bot-frontend")

# if __name__ == "__main__":
#     uvicorn.run("server:doc_server", port=PORT, reload=True)