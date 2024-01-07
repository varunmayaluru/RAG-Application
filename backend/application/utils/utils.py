import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from typing import Optional
import streamlit as st
import uuid
import requests
from bs4 import BeautifulSoup
from hashlib import md5
from typing import List
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def get_hash_value(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

def validate_qdrant_scroll_results(url: str, api_key: str, collection_name: str, source_hash: str, limit: int = 1) -> Optional[dict]:
    """
    Scrolls through documents in a Qdrant collection based on a specified source hash.

    Parameters:
    - url (str): The URL of the Qdrant service.
    - api_key (str): API key for authentication with the Qdrant service.
    - collection_name (str): Name of the collection to scroll through.
    - source_hash (str): The source hash to filter documents by.
    - limit (int, optional): The number of documents to return. Default is 1.

    Returns:
    - dict or None: The scrolled documents or None if an error occurs.

    Raises:
    - Exception: If there is an issue with the Qdrant client or the scroll operation.
    """
    try:
        # Create a Qdrant client instance
        qdrant_client = QdrantClient(
            url,
            api_key=api_key,
        )

        # Perform the scroll operation
        response = qdrant_client.scroll(
            collection_name=collection_name,
            scroll_filter=Filter(
                should=[
                    FieldCondition(
                        key="metadata.hash", match=MatchValue(value=source_hash)
                    ),
                ],
            ),
            limit=limit
        )

        # Check if the response contains records
        if response[1] is None or len(response[1]) == 0:
            return False
        else:
            return True

    except Exception as e:
        # Handle potential errors gracefully
        print(f"An error occurred: {e}")
        return None

def get_or_create_session_id():
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid.uuid4())
    return st.session_state

def url_loader(url: str) -> List[Document]:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the response is successful and the content type is HTML
        if response.status_code == 200 and 'text/html' in response.headers['Content-Type']:
            # Parse HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text from the parsed HTML
            text = soup.get_text(separator='\n')
            
            # Calculate hash value of the content
            hash_value = md5(text.encode()).hexdigest()

            # Create and return a list containing a Document object
            return [Document(page_content=text, metadata={"source": url, "hash": hash_value})]
        else:
            # Return an empty list if the URL does not point to an HTML document or the request failed
            return []
        
def split_text(doc: Document, chunk_size: int = 1000, chunk_overlap: int = 200):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True)
    splits = text_splitter.split_documents(doc)
    return splits

def main():
    url = st.text_input("Or enter a URL here and click on Process", type  = "default")
    data = {"url": url} if url else {}
    url = data.get('url')
    docs = url_loader(url)
    texts, metadatas = [], []
    for doc in docs:
        texts.append(doc.page_content)
        metadatas.append(doc.metadata)
    st.write(texts)
    st.write(metadatas)
    

# def split_documents(self, documents: Iterable[Document]) -> List[Document]:
#         """Split documents."""
#         texts, metadatas = [], []
#         for doc in documents:
#             texts.append(doc.page_content)
#             metadatas.append(doc.metadata)
#         return self.create_documents(texts, metadatas=metadatas)

def split_text(doc: Document, chunk_size: int = 1000, chunk_overlap: int = 200):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True)
        splits = text_splitter.split_documents(doc)
        return splits

if __name__ == "__main__":
    # call get_or_create_session_id to create a session_id
    # print(get_or_create_session_id())
    # call url_loader to load the url
    # docs = url_loader("https://www.ghx.com/the-healthcare-hub/healthcare-inventory-management/")
    # splits = split_text(docs)
    # print(splits[0])
    main()