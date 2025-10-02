from importlib.resources import files
from pathlib import Path

TAXI_CSV_PATH = files("taxipred").joinpath("data/taxi_trip_pricing.csv")
CLEANED_CSV_PATH = files("taxipred").joinpath("data/cleaned_data_v2.csv")
#CLEANED_CSV_PATH = "src/taxipred/data/cleaned_data_v2.csv"
#DATA_PATH = Path(__file__).parents[1] / "data"