from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from typing import Optional

# Initialize FastAPI app
app = FastAPI()

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PatientRecords')

# Define Patient model
class Patient(BaseModel):
    id: str
    name: str
    age: int
    email: Optional[str] = None
    medical_history: Optional[str] = None

@app.post("/patients/")
async def create_patient(patient: Patient):
    try:
        table.put_item(Item=patient.dict())
        return {"message": "Patient record created successfully", "patient_id": patient.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    try:
        response = table.get_item(Key={'id': patient_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Patient not found")
        return response['Item']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))