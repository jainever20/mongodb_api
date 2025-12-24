from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient 
from bson import ObjectId
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client["euron"]
euron_data = db["euron_coll"]

app = FastAPI()

class EuronData(BaseModel):
    name: str
    phone: int
    city: str
    course: str

@app.post("/euron/insert")
async def eurin_data_insert_helper(data: EuronData):
    result = await euron_data.insert_one(data.dict())
    return str(result.inserted_id)

def doc_helper(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@app.get("/euron/getdata")
async def get_euron_data():
    items = []
    cursor = euron_data.find({})
    async for document in cursor:
        items.append(doc_helper(document))
    return items

@app.delete("/euron/delete/{id}")
async def delete_records(id:str):
    result = await euron_data.delete_one({"_id":ObjectId(id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404,detail="Record not found")
    
    return {"message":"Record deleted successfully"}


class UpdateData(BaseModel):
    name: Optional[str] = None
    phone: Optional[int] = None
    city: Optional[str] = None
    course: Optional[str] = None

@app.put("/euron/update/{id}")
async def update_records(id : str, data:UpdateData):
    updated_data = {k:v for k,v in data.dict().items() if v is not None}

    if not updated_data:
        raise HTTPException(status_code=400,detail="No data provided to update")
    
    result = await euron_data.update_one(
        {"_id":ObjectId(id)},
        {"$set": updated_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")

    return {"message": "Record updated successfully"}
