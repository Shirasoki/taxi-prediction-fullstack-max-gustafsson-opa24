from taxipred.utils.constants import TAXI_CSV_PATH, CLEANED_CSV_PATH
import pandas as pd
import json
from pydantic import BaseModel, Field
from typing import Annotated



class TaxiData:
    def __init__(self):
        self.df = pd.read_csv(CLEANED_CSV_PATH)

    def to_json(self):
        return json.loads(self.df.to_json(orient = "records"))
    
class TaxiInput(BaseModel):
    Trip_Distance_km: float = Field(ge=1.2, le=50)
    Base_Fare: float = Field(ge=2, le=5)
    Per_Km_Rate: float = Field(ge=0.5, le=2)
    Per_Minute_Rate: float = Field(ge=0.1, le=0.5)
    Trip_Duration_Minutes: float = Field(ge=5, le=120)

class PredictionResponse(BaseModel):
    Predicted_Price: float

class TaxiFareOutput(BaseModel):
    Base_Fare: float = Field(ge=2, le=5)
    Per_Km_Rate: float = Field(ge=0.5, le=2)
    Per_Minute_Rate: float = Field(ge=0.1, le=0.5)

