from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3

app = FastAPI()
sns = boto3.client('sns')

class Notification(BaseModel):
    phone_number: str
    message: str

@app.post("/notifications/")
async def send_notification(notification: Notification):
    try:
        response = sns.publish(
            PhoneNumber=notification.phone_number,
            Message=notification.message
        )
        return {
            "message": "Notification sent successfully",
            "message_id": response['MessageId']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))