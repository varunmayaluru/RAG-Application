import streamlit as st
# from dotenv import load_dotenv
# from app import app
import requests
# import FastAPI app from backend
from app import app
import os

# token = None

def main():
    # global token
    # load_dotenv()
    st.set_page_config(page_title="Chat with Your Document", page_icon = "📚")

    st.header("Chat with Your Multiple Documents")
    # user_question = st.text_input("Ask a question about your document", disabled=not process_completed, key="user_question_before")

    # user_question = st.text_input("Ask a question about your document", key="user_question")
    if 'token' not in st.session_state:
        st.session_state['token'] = None
    
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

        # docs = st.file_uploader(
        #     "Upload your documents here and click on Process", type=["pdf", "txt", "docx"], accept_multiple_files=True)
        # if st.button("Process"):
        #     with st.spinner(text="Loading and indexing the docs - hang tight! This should take 1-2 minutes."):
        #         if docs:
        #             # Prepare the files in the correct format for the request
        #             files = [("files", (file.name, file, file.type)) for file in docs]

        #             # URL of your FastAPI endpoint
        #             url = 'http://127.0.0.1:8000/pdf-reader'

        #             # Make the request
        #             response = requests.post(url, files=files)

        #             # Handle the response
        #             if response.status_code == 200:
        #                 st.success('Files processed successfully!')
        #                 # st.json(response.json())

        #                 # Store the token
        #                 st.session_state['token'] = response.json().get('token')
                        
                        
        #             else:
        #                 st.error('An error occurred while processing the files.')
                        
        #         else:
        #             st.warning('Please upload at least one file.')

        docs = st.file_uploader(
            "Upload your documents here and click on Process", type=["pdf", "txt", "docx"], accept_multiple_files=True)

        url = st.text_input("Or enter a URL here and click on Process", type  = "default")

        if st.button("Process"):
            with st.spinner(text="Loading and indexing the docs - hang tight! This should take 1-2 minutes."):
                if docs or url:
                    # Prepare the files in the correct format for the request
                    files = [("files", (file.name, file, file.type)) for file in docs] if docs else []
                    params = {
                        "url": url,
                        "openai_api_key": openai_api_key,
                        "qdrant_url": qdrant_url,
                        "qdrant_api_key": qdrant_api_key,
                        "qdrant_collection_name": qdrant_collection_name
                    } 

                    # URL of your FastAPI endpoint
                    endpoint = 'http://127.0.0.1:8000/pdf-reader'

                    
                    # url = data.get('url')
                    # print("URL is: ", url)
                    # Make the request
                    response = requests.post(endpoint, data = params ,files=files)
                
                    # Handle the response
                    if response.status_code == 200:
                        st.success('Files processed successfully!')
                        # st.json(response.json())

                        # Store the token
                        st.session_state['token'] = response.json().get('token')
                    else:
                        st.error('An error occurred while processing the files.')
                else:
                    st.warning('Please upload at least one file or enter a URL.')
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    with st.chat_message("assistant"):
        st.write("Hello 👋 Welcome to Chat with your Document")

    # Display the chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    message_placeholder = st.empty()  # Create the message_placeholder outside the loop

    # prompt = st.chat_input("Ask your document 💭")
    if prompt:= st.chat_input("Ask your document 💭"):
        # Add the user's message to the chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
        # URL of your FastAPI endpoint
        url = 'http://127.0.0.1:8000/ask-question'

        data = {
            "token": str(st.session_state['token']),
            "question": str(prompt)
        }

        # Send a request to the API and get the response
        response = requests.post(url, json=data)
        full_response += response.json()["response"]
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()

