from fastapi import FastAPI, Request, WebSocket
from pydantic import BaseModel
from app.client import answer_question
# import uvicorn

# PORT = 8000
doc_server = FastAPI()

class QueryRequest(BaseModel):
    query: str

@doc_server.post("/ask")
def ask(request: QueryRequest):
    answer = answer_question(request.query)
    return {"answer": answer}

@doc_server.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        answer = answer_question(data)
        await websocket.send_text(answer)

# if __name__ == "__main__":
#     uvicorn.run("server:doc_server", port=PORT, reload=True)