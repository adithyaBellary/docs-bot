import urllib.parse
from langchain_community.document_loaders import ScrapingAntLoader
from langchain_text_splitters import HTMLSemanticPreservingSplitter, RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from dotenv import load_dotenv
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import os
import urllib
import tiktoken

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ROOT = "https://react-hook-form.com/docs"
SCRAPING_ANT_API_KEY = os.getenv("SCRAPING_ANT_API_KEY")

enc = tiktoken.encoding_for_model("gpt-4")

def get_all_links(root = ROOT):
  links = set()
  MAX_DEPTH = 2
  ROOT_SPLIT = urllib.parse.urlsplit(root)
  ROOT_URL_LOCATION = ROOT_SPLIT.netloc
  ROOT_PATH = ROOT_SPLIT.path

  def traverse(url=ROOT, depth=0):
    if depth > MAX_DEPTH:
      return
    
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")

    for link in soup.find_all("a"):
      href = link.get("href")
      url = urllib.parse.urlsplit(href)
      if url.netloc and url.netloc != ROOT_URL_LOCATION:
        # avoid external links
        continue
      if not url.path.startswith(ROOT_PATH):
        # avoid links that do not start with the root path
        continue
      if url.path not in links:
        links.add(url.path)
        print(f"found: {url.path}")
        traverse(urllib.parse.urljoin(root, url.path), depth + 1)

  traverse(root, 0)

  return [urllib.parse.urljoin(root, link) for link in links]

def ingest_documentation():
  URL = "https://react-hook-form.com/docs/useformstate"
  links = [URL]

  resp = requests.get(f"https://api.scrapingant.com/v2/general?url={URL}&x-api-key={SCRAPING_ANT_API_KEY}")
  soup = BeautifulSoup(resp.text, "html.parser")
  html = soup.prettify()
  doc = Document(page_content=html, metadata={"source": URL})

  content = [doc]

  headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
    ("h4", "Header 4"),
  ]

  semantic_splitter = HTMLSemanticPreservingSplitter(
    headers_to_split_on=headers_to_split_on,
    max_chunk_size=1000,
    separators=["\n\n", "\n"],
  )
  fallback_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", '.', ' '], chunk_size=1000, chunk_overlap=200)

  split_docs = []
  for doc in content:
    split_doc = semantic_splitter.split_text(doc.page_content)
    for d in split_doc:
      d.metadata = d.metadata | doc.metadata
      if (len(d.page_content) > 1500):
        smaller_docs = fallback_splitter.split_documents([d])
        for s in smaller_docs:
          split_docs.append(s)
      else:
        split_docs.append(d)

  embeddings = OpenAIEmbeddings()
  vector_store = FAISS.from_documents(split_docs, embeddings)
  vector_store.save_local("faiss_local")

def answer_question():
  query = "What are all the fields that the useFormState returns?"
  embeddings = OpenAIEmbeddings()
  vector_store = FAISS.load_local("faiss_local", embeddings, allow_dangerous_deserialization=True)
  docs = vector_store.similarity_search(query, k=4)

  context = "\n\n".join([f"Source: {doc.metadata}\n{doc.page_content}" for doc in docs])

  prompt = f"""You are a helpful documentation assistant. Answer any and all quesitons based only on the context below. Do not go elsewhere for information. Please cite the source of section where you got your answer from.
    Context: {context}

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

  print(response.choices[0].message.content.strip())



