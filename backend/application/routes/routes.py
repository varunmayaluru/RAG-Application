from backend.application.utils.rag import DocReader
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uuid
from backend.application.utils.utils import validate_qdrant_scroll_results, get_or_create_session_id
from dotenv import load_dotenv
import os
import streamlit as st
import secrets
from uuid import uuid4
import datetime
import jwt

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

pdf_reader_router = APIRouter()

# Assuming a global store (can be a database or in-memory store)
global_data_store = {}

@pdf_reader_router.post("/pdf-reader")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    # Generate a unique identifier
    unique_id = str(uuid4())
    all_splits = []
    already_uploaded_files = []
    for file in files:
        doc_reader = DocReader(file=file.file)
        docs = doc_reader.pdf_loader()
        splits = doc_reader.split_text(docs)
        # # Check if any split has a hash value already present in validate_qdrant_scroll_results
        # if any(validate_qdrant_scroll_results(QDRANT_URL,QDRANT_API_KEY, "my_documents" ,split.metadata.get("hash"),1) for split in splits):
        #     already_uploaded_files.append(file.filename)
        #     continue
        all_splits.extend(splits)
    # print(already_uploaded_files)
    # if already_uploaded_files:
    #     return {"message": f"The following files are already uploaded: {', '.join(already_uploaded_files)}", "id": unique_id}

    vectorstore = doc_reader.create_vector_store(all_splits)
    retriever = doc_reader.create_retriever(vectorstore)
    prompt = doc_reader.create_qa_prompt()
    llm = doc_reader.create_llm()
    rag_chain = doc_reader.create_rag_chain_with_history(doc_reader.contextualized_question, retriever, doc_reader.format_docs, prompt, llm)
    
    # Store the session data
    global_data_store[unique_id] = (rag_chain, doc_reader)

    # # Generate a JWT token
    # expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
    # token = jwt.encode({"session_id": unique_id, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)

    # # make rag_chain and doc_reader as json serializable
    # rag_chain = rag_chain.to_dict()
    # doc_reader = doc_reader.to_dict()
    return {"message": "PDFs processed", "token": unique_id}

@pdf_reader_router.post("/ask-question")
async def ask_question(token: str, question: str):
    try:
        # Decode the token
        # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # session_id = payload.get("session_id")
        unique_id = token
        if unique_id in global_data_store:
            rag_chain, doc_reader = global_data_store[unique_id]
            response = doc_reader.ask_contextual_question(rag_chain, question)
            return {"response": response}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
