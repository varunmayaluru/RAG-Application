# fastapi_app.py

from fastapi import FastAPI, HTTPException

app = FastAPI()

# Global dictionary to share data between endpoints
shared_data = {}

from pydantic import BaseModel

class Item(BaseModel):
    value: str

@app.post("/set/{key}")
async def set_data(key: str, item: Item):
    shared_data[key] = item.value
    return {"message": f"Data set for key {key}"}


@app.get("/get/{key}")
async def get_data(key: str):
    if key not in shared_data:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": shared_data[key]}
