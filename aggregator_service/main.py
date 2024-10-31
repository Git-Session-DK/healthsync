from fastapi import FastAPI, HTTPException
import boto3
from datetime import datetime, timedelta

app = FastAPI()
redshift_client = boto3.client('redshift-data')
dynamodb = boto3.resource('dynamodb')

@app.get("/aggregate/daily-appointments")
async def aggregate_daily_appointments():
    try:
        query = """
        INSERT INTO appointment_metrics (date, total_appointments, completed_appointments)
        SELECT 
            DATE(appointment_time) as date,
            COUNT(*) as total_appointments,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_appointments
        FROM appointments
        WHERE DATE(appointment_time) = CURRENT_DATE - 1
        GROUP BY DATE(appointment_time)
        """
        
        response = redshift_client.execute_statement(
            ClusterIdentifier='your-cluster-id',
            Database='healthsync_analytics',
            Sql=query
        )
        return {"message": "Daily aggregation completed", "execution_id": response['Id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))