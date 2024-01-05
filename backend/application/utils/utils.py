import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from typing import Optional
from dotenv import load_dotenv
import os
import streamlit as st
import uuid

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

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

if __name__ == "__main__":
    # call get_or_create_session_id to create a session_id
    print(get_or_create_session_id())