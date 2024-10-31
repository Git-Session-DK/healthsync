from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from datetime import datetime
from typing import Optional

app = FastAPI()
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Appointments')

class Appointment(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    appointment_time: datetime
    status: str
    notes: Optional[str] = None

@app.post("/appointments/")
async def create_appointment(appointment: Appointment):
    try:
        table.put_item(Item=appointment.dict())
        return {"message": "Appointment created successfully", "appointment_id": appointment.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/appointments/{appointment_id}")
async def get_appointment(appointment_id: str):
    try:
        response = table.get_item(Key={'id': appointment_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return response['Item']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))