from fastapi import FastAPI, Request
from pydantic import BaseModel
from app.client import answer_question

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask(request: QueryRequest):
    answer = answer_question(request.query)
    return {"answer": answer}