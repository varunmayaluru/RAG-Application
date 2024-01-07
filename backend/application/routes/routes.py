from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uuid
import os
from backend.application.utils.rag import DocReader
from typing import List, Optional

# Define Pydantic models
class PDFUploadResponse(BaseModel):
    message: str
    token: str

class AskQuestionRequest(BaseModel):
    token: str
    question: str

class AskQuestionResponse(BaseModel):
    response: str

class PDFReaderRequest(BaseModel):
    url: Optional[str]
    files: Optional[List[UploadFile]]

# Initialize APIRouter
pdf_reader_router = APIRouter()

# Global data store
global_data_store = {}

@pdf_reader_router.post("/pdf-reader", response_model=PDFUploadResponse)
# async def upload_pdfs(files: Optional[List[UploadFile]] = File(None), url: Optional[str] = None):
async def upload_pdfs (files:  List[UploadFile] = File(None), url: str = Form(None), openai_api_key: str = Form(None), qdrant_url: str = Form(None), qdrant_api_key: str = Form(None), qdrant_collection_name: str = Form(None)):
    if files is None and url is None:
        raise HTTPException(status_code=400, detail="Either files or url must be provided")

    unique_id = str(uuid.uuid4())
    all_splits = []

    os.environ["OPENAI_API_KEY"] = openai_api_key
    os.environ["QDRANT_URL"] = qdrant_url
    os.environ["QDRANT_API_KEY"] = qdrant_api_key
    os.environ["QDRANT_COLLECTION_NAME"] = qdrant_collection_name

    OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

    if url is not None:
        doc_reader = DocReader()
        docs = doc_reader.url_loader(url)
        splits = doc_reader.split_text(docs)
        all_splits.extend(splits)
    else:
        for file in files:
            doc_reader = DocReader(file=file.file)
            _, file_extension = os.path.splitext(file.filename)

            if file_extension == '.pdf':
                docs = doc_reader.pdf_loader()
            elif file_extension in ['.docx', '.doc']:
                docs = doc_reader.docx_loader()
            elif file_extension == '.txt':
                docs = doc_reader.txt_loader()
            splits = doc_reader.split_text(docs)
            all_splits.extend(splits)
    vectorstore = doc_reader.create_vector_store(all_splits)
    retriever = doc_reader.create_retriever(vectorstore)
    prompt = doc_reader.create_qa_prompt()
    llm = doc_reader.create_llm()
    rag_chain = doc_reader.create_rag_chain_with_history(doc_reader.contextualized_question, retriever, doc_reader.format_docs, prompt, llm)
    global_data_store[unique_id] = (rag_chain, doc_reader)

    return {"message": "Documents processed", "token": unique_id}

@pdf_reader_router.post("/ask-question", response_model=AskQuestionResponse)
async def ask_question(request: AskQuestionRequest):
    unique_id = request.token
    if unique_id in global_data_store:
        rag_chain, doc_reader = global_data_store[unique_id]
        response = doc_reader.ask_contextual_question(rag_chain, request.question)
        return {"response": response}
    else:
        raise HTTPException(status_code=404, detail="Session not found")
