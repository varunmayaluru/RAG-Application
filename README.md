<!-- # RAG-Application
Retrieval Augmented Generation 

# Pre-requisite
Make sure you are in root folder of project

## Create Virtual environment
python3 -m venv .venv

## Activate virtual environment
source .venv/bin/activate

## Install required packages
pip3 install -r requirements.txt

## Pre-requisite make sure backend service is up and running
uvicorn app:app --reload --host 0.0.0.0 --port 8000

## (Optional) Incase if you want to use Streamlit app 
streamlit run main.py -->

# RAG-Application: Retrieval Augmented Generation

## Prerequisites
Ensure you are in the root folder of the project before proceeding.

## Setting Up the Environment

1. **Create a Virtual Environment**
   ```sh
   python3 -m venv .venv
2. **Activate the Virtual Environment**
   ```sh
   source .venv/bin/activate
3. **Install Required Packages**
   ```sh
   pip3 install -r requirements.txt
4. **Running the Backend Service**
   ```sh
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
5. **(Optional) Incase if you want to use Streamlit app**
   ```sh
   streamlit run main.py
