from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uuid
from dotenv import load_dotenv
import os
from backend.application.utils.rag import DocReader

# Load environment variables
load_dotenv()

# Define Pydantic models
class PDFUploadResponse(BaseModel):
    message: str
    token: str

class AskQuestionRequest(BaseModel):
    token: str
    question: str

class AskQuestionResponse(BaseModel):
    response: str

# Initialize APIRouter
pdf_reader_router = APIRouter()

# Global data store
global_data_store = {}

@pdf_reader_router.post("/pdf-reader", response_model=PDFUploadResponse)
async def upload_pdfs(files: list[UploadFile] = File(...)):
    unique_id = str(uuid.uuid4())
    all_splits = []
    for file in files:
        doc_reader = DocReader(file=file.file)
        docs = doc_reader.pdf_loader()
        splits = doc_reader.split_text(docs)
        all_splits.extend(splits)

    # Process the PDF and store the session data
    vectorstore = doc_reader.create_vector_store(all_splits)
    retriever = doc_reader.create_retriever(vectorstore)
    prompt = doc_reader.create_qa_prompt()
    llm = doc_reader.create_llm()
    rag_chain = doc_reader.create_rag_chain_with_history(doc_reader.contextualized_question, retriever, doc_reader.format_docs, prompt, llm)
    global_data_store[unique_id] = (rag_chain, doc_reader)

    return {"message": "PDFs processed", "token": unique_id}

@pdf_reader_router.post("/ask-question", response_model=AskQuestionResponse)
async def ask_question(request: AskQuestionRequest):
    unique_id = request.token
    if unique_id in global_data_store:
        rag_chain, doc_reader = global_data_store[unique_id]
        response = doc_reader.ask_contextual_question(rag_chain, request.question)
        return {"response": response}
    else:
        raise HTTPException(status_code=404, detail="Session not found")
