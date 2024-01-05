# import required libraries
from fastapi import FastAPI
from backend.application.routes.routes_v1 import pdf_reader_router
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


from fastapi import FastAPI

app = FastAPI(
    title="PDF RAG LLM API",
    description="An API to extract text from a PDF file, split the text into chunks, retrieve documents from the text chunks, create a RAG chain, and generate a summary of the PDF file.",
    version="0.1.0",
)

app.include_router(pdf_reader_router, tags=["PDF Reader"])

# Run the API with uvicorn
# uvicorn backend.app:app --reload --host

