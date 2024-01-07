# from rag import DocReader
from fastapi import APIRouter, File, UploadFile, HTTPException, Query

# all_splits = []
# # doc_reader = DocReader()
# url = "https://www.ghx.com/the-healthcare-hub/healthcare-inventory-management/"
# docs = doc_reader.url_loader(url)
# for doc in docs:
#         print(doc)
# #         splits = doc_reader.split_text(doc)
# #         all_splits.extend(splits)
# # print(all_splits)

params = {
    "url": "https://www.ghx.com/the-healthcare-hub/healthcare-inventory-management/"
}

import requests
url = "https://www.ghx.com/the-healthcare-hub/healthcare-inventory-management/"
endpoint = 'http://127.0.0.1:8000/pdf-reader'
response = requests.post(endpoint, data=params)
print(response.json())

