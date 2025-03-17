# Required packages:
# pip install fastapi uvicorn pandas numpy transformers pydantic python-multipart

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import uvicorn
import json
import os
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

# Initialize FastAPI app
app = FastAPI(title="Forecasting API", description="API for time series forecasting using Hugging Face models")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define input and output models
class TimeSeriesData(BaseModel):
    dates: List[str]
    values: List[float]
    horizon: int = 7  # Default forecast horizon (7 days/periods ahead)

class ForecastResult(BaseModel):
    forecast_dates: List[str]
    forecast_values: List[float]
    model_used: str

# Download and load model on startup
@app.on_event("startup")
async def load_model():
    global forecasting_model, tokenizer
    
    # For this example, we'll use a text classification model that can be adapted for forecasting
    # You would replace this with an actual forecasting model like TimeGPT or a custom model
    model_name = "distilbert-base-uncased"  # Placeholder model
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        forecasting_model = AutoModelForSequenceClassification.from_pretrained(model_name)
        app.state.model_info = {"name": model_name, "type": "classification"}
    except Exception as e:
        print(f"Error loading model: {e}")
        # Fallback to simpler model if main one fails
        try:
            model_name = "prajjwal1/bert-tiny"  # Smaller fallback model
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            forecasting_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            app.state.model_info = {"name": model_name, "type": "classification"}
        except Exception as e2:
            print(f"Error loading fallback model: {e2}")
            app.state.model_info = {"name": "none", "type": "none"}

# Simple forecasting endpoint using model (for demo purposes)
@app.post("/forecast/", response_model=ForecastResult)
async def create_forecast(data: TimeSeriesData):
    # In a real implementation, you would:
    # 1. Preprocess the time series data
    # 2. Feed it to your forecasting model
    # 3. Return the predictions
    
    # For demo purposes, we'll use a simple naive forecast
    # (In a real app, you'd use the loaded model)
    
    try:
        # Convert input data to pandas Series
        ts_data = pd.Series(data.values, index=pd.to_datetime(data.dates))
        
        # Generate forecast dates (continuing from the last date in the input)
        last_date = pd.to_datetime(data.dates[-1])
        freq = pd.infer_freq(pd.to_datetime(data.dates))
        if not freq:
            freq = 'D'  # Default to daily if frequency can't be inferred
            
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), 
                                       periods=data.horizon, 
                                       freq=freq)
        
        # Simple forecasting logic (for demo - replace with actual model inference)
        # Here we're just using a naive forecast based on the last few values
        last_values = ts_data[-5:]
        forecast_values = []
        
        for _ in range(data.horizon):
            # Simple moving average forecast
            next_value = last_values.mean() + np.random.normal(0, 0.1)
            forecast_values.append(float(next_value))
            last_values = pd.concat([last_values[1:], pd.Series([next_value])])
        
        return ForecastResult(
            forecast_dates=[str(date.date()) for date in forecast_dates],
            forecast_values=forecast_values,
            model_used=app.state.model_info["name"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting error: {str(e)}")

# Upload CSV data for forecasting
@app.post("/forecast-from-csv/", response_model=ForecastResult)
async def forecast_from_csv(
    file: UploadFile = File(...),
    date_column: str = Form(...),
    value_column: str = Form(...),
    horizon: int = Form(7)
):
    try:
        # Read the uploaded CSV
        content = await file.read()
        df = pd.read_csv(pd.io.StringIO(content.decode('utf-8')))
        
        # Validate required columns
        if date_column not in df.columns or value_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"CSV must contain {date_column} and {value_column} columns")
        
        # Convert to TimeSeriesData format
        dates = df[date_column].astype(str).tolist()
        values = df[value_column].astype(float).tolist()
        
        # Use the same forecasting logic
        data = TimeSeriesData(dates=dates, values=values, horizon=horizon)
        return await create_forecast(data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV processing error: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": app.state.model_info
    }

# Run the API server
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
