import requests 
from urllib.parse import urljoin

def read_api_endpoint(endpoint = "/read", base_url = "http://127.0.0.1:8000"):
    url = urljoin(base_url, endpoint)
    response = requests.get(url)
    
    return response


def post_api_endpoint(endpoint = "/post", base_url = "http://127.0.0.1:8000"):
    url = urljoin(base_url, endpoint)
    response = requests.post(url)
    
    return response

def predict_api_endpoint(data, endpoint = "/predict", base_url = "http://127.0.0.1:8000"):
    url = urljoin(base_url, endpoint)
    response = requests.post(url, json=data)
    
    return response


# TODO:
# post_api_endpoint