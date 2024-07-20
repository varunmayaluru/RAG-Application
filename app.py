# import required libraries
from fastapi import FastAPI
from backend.application.routes.routes import pdf_reader_router


from fastapi import FastAPI

app = FastAPI(
    title="PDF RAG LLM API",
    description="An API to extract text from a PDF file, split the text into chunks, retrieve documents from the text chunks, create a RAG chain, and generate a summary of the PDF file.",
    version="0.1.0",
)

app.include_router(pdf_reader_router, tags=["PDF Reader"])

# Run the API with uvicorn
# uvicorn backend.app:app --reload --host
# uvicorn app:app --reload --host 0.0.0.0 --port 8000

