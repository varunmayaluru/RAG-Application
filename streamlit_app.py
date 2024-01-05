# streamlit_app.py

import streamlit as st
import requests

API_URL = "http://localhost:8000"  # URL of the FastAPI app

st.title("Streamlit-FastAPI Interaction")

# Input fields for setting data
key_to_set = st.text_input("Key to set")
value_to_set = st.text_input("Value to set")
if st.button("Set Data"):
    response = requests.post(f"{API_URL}/set/{key_to_set}", json={"value": value_to_set})
    st.write(response.json())


st.write("---")

# Input field for getting data
key_to_get = st.text_input("Key to get")
if st.button("Get Data"):
    response = requests.get(f"{API_URL}/get/{key_to_get}")
    if response.status_code == 200:
        st.write(response.json())
    else:
        st.error("Error: " + response.json().get('detail', 'Unknown error'))

