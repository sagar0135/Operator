from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List, Optional
from pydantic import BaseModel, validator, ValidationError
import urllib.parse
from bson import ObjectId
from bson import json_util

app = FastAPI()

# MongoDB Atlas connection string
username = urllib.parse.quote_plus("19276146")
password = urllib.parse.quote_plus("Sagar@1234")
client = MongoClient(f"mongodb+srv://{username}:{password}@cluster1.hojcyfx.mongodb.net")
db = client["operator"]
collection = db["users"]
collection_1 = db["user"]
collection_2 = db["university"]
collection_3 = db["surveys"]

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/login/", tags=["Login"])
async def login(user: UserLogin):
    username = user.username
    password = user.password
    
    user_data = collection.find_one({"username": username})
    if not user_data:
        raise HTTPException(status_code=404, detail="Invalid username or password")
    
    if user_data["password"]!= password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {"message": "Login successful"}

class University(BaseModel):
    name: str
    location: str
    contact_email: str
    username: str
    university_id: str
    university_name: str
    is_active: bool

@app.post("/university-account", response_model=University, tags=["Institutes"])
async def create_university_account(university: University):
    if collection_2.find_one({"name": university.name}):
        raise HTTPException(status_code=400, detail="University with this name already exists")
    
    result = collection_2.insert_one(university.dict())
    return {"message": "University created successfully", "university_id": str(result.inserted_id)}

@app.get("/university/", response_model=list[University], tags=["Institutes"])
async def get_university_name():
    university = list(collection_2.find({}))
    if university:
        return university
    else:
        raise HTTPException(status_code=404, detail="No universities found")

@app.put("/activate/{university_id}", response_model=None, tags=["User Management"])
async def activate_user(username: str):
    user = collection_2.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    collection_2.update_one({"username": username}, {"$set": {"is_active": True}})
    return {"message": f"User {username} activated successfully"}

@app.put("/deactivate/{university_id}", response_model=None, tags=["User Management"])
async def deactivate_user(username: str):
    user = collection_2.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    collection_2.update_one({"username": username}, {"$set": {"is_active": False}})
    return {"message": f"User {username} deactivated successfully"}

@app.put("/customize-account/{university_id}", response_model=University, tags=["User Management"])
async def customize_user_account(username: str, university_update: University):
    user = collection_2.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = university_update.dict(exclude_unset=True)
    collection_2.update_one({"username": username}, {"$set": update_data})

    updated_user = collection_2.find_one({"username": username})
    return updated_user

class Survey(BaseModel):
    university_id: str
    student_id: Optional[str] = None
    staff_id: Optional[str] = None
    Program: str
    Rank: List[str]
    survey_results: Optional[List[str]] = None
    statistical_data: Optional[str] = None

@app.post("/survey/create/", response_model=Survey, tags=["Survey"])
async def create_survey(survey: Survey):
    inserted_survey = collection_3.insert_one(survey.dict())
    return {"message": "Survey created successfully", "survey_id": str(inserted_survey.inserted_id)}

@app.get("/survey/results/", response_model=list[Survey], tags=["Survey"])
async def get_survey_results():
    survey = list(collection_3.find({}))
    if survey:
        return survey
    else:
        raise HTTPException(status_code=404, detail="Survey not found")

@app.post("/survey/{survey_id}/submit/", tags=["Survey"])
async def submit_survey_response(survey_id: str, response: str):
    survey = collection_3.find_one({"_id": survey_id})
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    collection_3.update_one({"_id": survey_id}, {"$push": {"survey_results": response}})
    return {"message": "Survey response submitted successfully"}

@app.post("/publish_results/{survey_id}/", tags=["Survey"])
async def publish_survey_results(survey_id: str):
    survey = collection_3.find_one({"_id": survey_id})
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    # Here you can add logic to publish survey results
    return {"message": "Survey results published successfully"}

@app.post("/statistical_analysis/", tags=["Statistical Analysis"])
async def perform_statistical_analysis(university_name: str, data: str):
    # Placeholder logic for statistical analysis
    return {"analysis_results": "Placeholder statistical analysis results"}