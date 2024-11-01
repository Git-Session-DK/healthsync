from fastapi import FastAPI, HTTPException
import boto3
from datetime import datetime, timedelta
from typing import Dict

app = FastAPI()
redshift_client = boto3.client('redshift-data')
dynamodb = boto3.resource('dynamodb')

CLUSTER_ID = 'your-cluster-id'
DATABASE = 'healthsync_analytics'

@app.get("/aggregate/daily-appointments")
async def aggregate_daily_appointments():
    try:
        # Appointments per doctor
        doctor_query = """
        INSERT INTO doctor_metrics (date, doctor_id, appointment_count, specialty)
        SELECT 
            DATE(appointment_time) as date,
            doctor_id,
            COUNT(*) as appointment_count,
            specialty
        FROM appointments
        WHERE DATE(appointment_time) = CURRENT_DATE - 1
        GROUP BY DATE(appointment_time), doctor_id, specialty
        """
        
        # Appointment frequency
        frequency_query = """
        INSERT INTO appointment_frequency (date, hour_of_day, appointment_count)
        SELECT 
            DATE(appointment_time) as date,
            EXTRACT(HOUR FROM appointment_time) as hour_of_day,
            COUNT(*) as appointment_count
        FROM appointments
        WHERE DATE(appointment_time) = CURRENT_DATE - 1
        GROUP BY DATE(appointment_time), EXTRACT(HOUR FROM appointment_time)
        """
        
        # Common symptoms by specialty
        symptoms_query = """
        INSERT INTO symptom_metrics (date, specialty, symptom, occurrence_count)
        SELECT 
            DATE(appointment_time) as date,
            specialty,
            symptom,
            COUNT(*) as occurrence_count
        FROM appointments
        CROSS JOIN UNNEST(symptoms) as t(symptom)
        WHERE DATE(appointment_time) = CURRENT_DATE - 1
        GROUP BY DATE(appointment_time), specialty, symptom
        """
        
        # Execute all queries
        responses = []
        for query in [doctor_query, frequency_query, symptoms_query]:
            response = redshift_client.execute_statement(
                ClusterIdentifier=CLUSTER_ID,
                Database=DATABASE,
                Sql=query
            )
            responses.append(response['Id'])
        
        return {
            "message": "Daily aggregation completed",
            "execution_ids": responses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/doctors")
async def get_doctor_metrics(date: str = None):
    try:
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
        query = f"""
        SELECT doctor_id, appointment_count, specialty
        FROM doctor_metrics
        WHERE date = '{date}'
        """
        
        response = redshift_client.execute_statement(
            ClusterIdentifier=CLUSTER_ID,
            Database=DATABASE,
            Sql=query
        )
        return {"date": date, "metrics": response['Id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
