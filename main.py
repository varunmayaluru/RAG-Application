import streamlit as st
from dotenv import load_dotenv
# from app import app
import requests
# import FastAPI app from backend
from app import app
import os

# token = None

def main():
    # global token
    load_dotenv()
    st.set_page_config(page_title="Chat with Your Document", page_icon = "📚")

    st.header("Chat with Your Multiple Documents")
    # user_question = st.text_input("Ask a question about your document", disabled=not process_completed, key="user_question_before")

    user_question = st.text_input("Ask a question about your document", key="user_question")
    if 'token' not in st.session_state:
        st.session_state['token'] = None

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    with st.sidebar:
        st.subheader("Your Documents")
        openai_api_key = st.text_input("OpenAI API Key", key="langchain_search_api_key_openai", type="password")
        qdrant_url = st.text_input("Enter Qdrant URL", key="qdrant_url")
        qdrant_api_key = st.text_input("Enter Qdrant API Key", key="qdrant_api_key", type="password")
        qdrant_collection_name = st.text_input("Enter Qdrant Collection Name", value="my_documents", key="qdrant_collection_name")
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if qdrant_url:
            os.environ["QDRANT_URL"] = qdrant_url
            QDRANT_URL = os.getenv("QDRANT_URL")
        if qdrant_api_key:
            os.environ["QDRANT_API_KEY"] = qdrant_api_key
            QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
        if qdrant_collection_name:
            os.environ["QDRANT_COLLECTION_NAME"] = qdrant_collection_name
            QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

        docs = st.file_uploader(
            "Upload your documents here and click on Process", type=["pdf", "txt", "docx"], accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner(text="Loading and indexing the docs - hang tight! This should take 1-2 minutes."):
                if docs:
                    # Prepare the files in the correct format for the request
                    files = [("files", (file.name, file, file.type)) for file in docs]

                    # URL of your FastAPI endpoint
                    url = 'http://127.0.0.1:8000/pdf-reader'

                    # Make the request
                    response = requests.post(url, files=files)

                    # Handle the response
                    if response.status_code == 200:
                        st.success('Files processed successfully!')
                        # st.json(response.json())

                        # Store the token
                        st.session_state['token'] = response.json().get('token')
                        
                        
                    else:
                        st.error('An error occurred while processing the files.')
                        
                else:
                    st.warning('Please upload at least one file.')
                    
    if user_question:
        while True:
            # user_question = st.text_input("Ask a question about your document", disabled=False, key="user_question_after")
            
            # URL of your FastAPI endpoint
            url = 'http://127.0.0.1:8000/ask-question'

            data = {
                "token": str(st.session_state['token']),
                "question": str(user_question)
            }
            print(data)
            # Send a request to the API and get the response
            response = requests.post(url, json=data)

            # Handle the response
            if response.status_code == 200:
                st.success('Question asked successfully!')
                st.json(response.json())
            else:
                st.error('An error occurred while asking the question.')

            # Ask the user if they want to continue
            continue_chat = st.button('Ask another question')
            if not continue_chat:
                break
    
              
if __name__ == "__main__":
    main()