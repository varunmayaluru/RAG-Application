from backend.application.utils.rag import DocReader
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import uuid
from backend.application.utils.utils import validate_qdrant_scroll_results
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

pdf_reader_router = APIRouter()

# Assuming a global store (can be a database or in-memory store)
global_data_store = {}

@pdf_reader_router.post("/pdf-reader")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    unique_id = str(uuid.uuid4())  # Generate a unique identifier
    all_splits = []
    already_uploaded_files = []
    for file in files:
        doc_reader = DocReader(file=file.file)
        docs = doc_reader.pdf_loader()
        splits = doc_reader.split_text(docs)
        # Check if any split has a hash value already present in validate_qdrant_scroll_results
        if any(validate_qdrant_scroll_results(QDRANT_URL,QDRANT_API_KEY, "my_documents" ,split.metadata.get("hash"),1) for split in splits):
            already_uploaded_files.append(file.filename)
            continue
        all_splits.extend(splits)
    print(already_uploaded_files)
    if already_uploaded_files:
        return {"message": f"The following files are already uploaded: {', '.join(already_uploaded_files)}", "id": unique_id}

    vectorstore = doc_reader.create_vector_store(all_splits)
    retriever = doc_reader.create_retriever(vectorstore)
    prompt = doc_reader.create_qa_prompt()
    llm = doc_reader.create_llm()
    rag_chain = doc_reader.create_rag_chain_with_history(doc_reader.contextualized_question, retriever, doc_reader.format_docs, prompt, llm)
    global_data_store[unique_id] = rag_chain, doc_reader
    return {"message": "PDFs processed", "id": unique_id}


@pdf_reader_router.post("/ask-question")
async def ask_question(question: str, id: str):  # Include ID as a parameter
    if id in global_data_store:
        rag_chain, doc_reader = global_data_store[id]
        response = doc_reader.ask_contextual_question(rag_chain, question)
        return {"response": response}
    else:
        return JSONResponse(content={"error": "Invalid ID"}, status_code=404)

