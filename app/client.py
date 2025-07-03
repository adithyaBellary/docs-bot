from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def answer_question(query, messages_archive=None):
  embeddings = OpenAIEmbeddings()
  vector_store = FAISS.load_local("faiss_local", embeddings, allow_dangerous_deserialization=True)
  docs = vector_store.similarity_search(query, k=4)

  context = "\n\n".join([f"Source: {doc.metadata}\n{doc.page_content}" for doc in docs])

  prompt = f"""You are a helpful documentation assistant. Answer any and all quesitons based only on the context below. Do not go elsewhere for information. Please cite the source of section where you got your answer from.
    Documentation Context: {context}

    Previous Messages Context: {messages_archive}

    Question: {query}"""

  response = client.chat.completions.create(
    model="gpt-4",
    messages=[
      {
        "role": "user", "content": prompt
      }
    ],
    temperature=0.2
  )

  answer = response.choices[0].message.content.strip()
  print(answer)
  return answer
