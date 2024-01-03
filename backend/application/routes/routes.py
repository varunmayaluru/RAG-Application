from backend.application.utils.rag import DocReader
from fastapi import FastAPI, APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import uuid

pdf_reader_router = APIRouter()

# Assuming a global store (can be a database or in-memory store)
global_data_store = {}

@pdf_reader_router.post("/pdf-reader")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    unique_id = str(uuid.uuid4())  # Generate a unique identifier
    all_splits = []
    for file in files:
        doc_reader = DocReader(file=file.file)
        docs = doc_reader.pdf_loader()
        splits = doc_reader.split_text(docs)
        all_splits.extend(splits)

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

