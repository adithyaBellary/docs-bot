import urllib.parse
from langchain_community.document_loaders import ScrapingAntLoader
from langchain_text_splitters import HTMLSemanticPreservingSplitter, RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
import os
import hashlib
import urllib

load_dotenv()

SCRAPING_ANT_API_KEY = os.getenv("SCRAPING_ANT_API_KEY")

ROOT = "https://react-hook-form.com/docs"

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

def scrape_docs(URL):
  # links = ["https://react-hook-form.com/docs/useformstate"]
  links = get_all_links(URL)
  content = []

  for link in links:
    hashed_link = hashlib.sha256(link.encode("utf-8")).hexdigest() + '.txt' 
    hashed_link_full = os.path.join("tmp", hashed_link)
    print(link, hashed_link_full)
    if os.path.exists(hashed_link_full):
      print('exists')
      with open(hashed_link_full, 'r') as file:
        html_from_file = file.read()
        doc = Document(page_content=html_from_file, metadata={"source": link})
    else:
      print('does not exist')
      resp = requests.get(f"https://api.scrapingant.com/v2/general?url={link}&x-api-key={SCRAPING_ANT_API_KEY}")
      soup = BeautifulSoup(resp.text, "html.parser")
      html = str(soup.prettify())

      with open(hashed_link_full, "x") as file:
        file.write(html)
      doc = Document(page_content=html, metadata={"source": link})

    content.append(doc)
    print(f"fetched: {link}")
  return content

def ingest_documentation(URL):
  document_content = scrape_docs(URL)

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
  for doc in document_content:
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

