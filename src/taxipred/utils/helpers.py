import requests 
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:8000"

def read_api_endpoint(endpoint = "/taxi/", base_url = BASE_URL):
    url = urljoin(base_url, endpoint)
    response = requests.get(url)
    
    return response


def post_api_endpoint(endpoint = "/taxi/post", base_url = BASE_URL):
    url = urljoin(base_url, endpoint)
    response = requests.post(url)
    
    return response

def predict_api_endpoint(data, endpoint = "/taxi/predict", base_url = BASE_URL):
    url = urljoin(base_url, endpoint)
    response = requests.post(url, json=data)
    
    return response


# TODO:
# post_api_endpoint
# testet