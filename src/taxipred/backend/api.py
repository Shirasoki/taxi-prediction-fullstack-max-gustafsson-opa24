from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData
from pydantic import BaseModel, conint, confloat
from datetime import datetime
from pathlib import Path
import joblib
import pandas as pd
import requests
from urllib.parse import urljoin
from taxipred.backend.data_processing import TaxiData, PredictionResponse, TaxiInput, TaxiFareOutput
from taxipred.utils.constants import TAXI_MODEL_PATH, CLEANED_CSV_PATH

app = FastAPI()

taxi_data = TaxiData()
BASE_URL = ("http://127.0.0.1:8000")

@app.get("/taxi/")
async def read_taxi_data():
    return taxi_data.to_json()

@app.post("/taxi/predict", response_model=PredictionResponse)
async def predict_taxi_price(payload: TaxiInput):
    data_to_predict = pd.DataFrame([payload.model_dump()])
    model = joblib.load(TAXI_MODEL_PATH)
    prediction = model.predict(data_to_predict)
    
    return {"Predicted_Price": prediction[0]}

@app.post("/taxi/fares/predict", response_model=TaxiFareOutput)
async def predict_taxi_fares(payload: TaxiInput):
    data_to_predict = pd.DataFrame([payload.model_dump()])
    model = joblib.load(TAXI_MODEL_PATH)
    prediction = model.predict(data_to_predict)
    
    return {
        "Base_Fare": prediction[0][0],
        "Per_Km_Rate": prediction[0][1],
        "Per_Minute_Rate": prediction[0][2]
    }

#test test test
