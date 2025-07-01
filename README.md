# [WIP] AI API Documentation Assistant

This idea came about when I was working on other projects and noticed that I was spending a lot of time looking through API documentation. In general, it was pretty specific and direct questions that I needed answered, such as what the payload objects looked like, and the proper syntax of helper functions. This seemed to me a task perfectly suited for an LLM.

Right now there is no interactive chat feature, but that is currently being developed. 

## Notable design choices

The goal of this assistant is to be able to answer questions on the entirety of the API Documentation. However, when it needs to answer a question, it usually needs to go to a specific portion of the docs. So, to make that possible, I scrape the webpage and break up the text into semantic chunks. Then, I use FAISS-based vector indexing to find the `k` most relevant parts of the whole set of documents to pass in as context to the GPT call. 

## Coming Soon

This is still currently being worked on! So please check back in regularly. 

Some things that are currently in flight:
- Interactive chat 
- deploying this to AWS 
- tbd