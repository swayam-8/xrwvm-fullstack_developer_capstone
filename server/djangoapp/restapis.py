"""HTTP adapters for the dealership and sentiment microservices."""
import os
from urllib.parse import quote
import requests

backend_url = os.getenv('backend_url', 'http://127.0.0.1:3030').rstrip('/')
sentiment_analyzer_url = os.getenv('sentiment_analyzer_url', 'http://127.0.0.1:5050').rstrip('/')

def get_request(endpoint, **kwargs):
    response = requests.get(f'{backend_url}/{endpoint.lstrip("/")}', params=kwargs, timeout=15)
    response.raise_for_status()
    return response.json()

def analyze_review_sentiments(text):
    response = requests.get(f'{sentiment_analyzer_url}/analyze/{quote(text, safe="")}', timeout=15)
    response.raise_for_status()
    return response.json()

def post_review(data_dict):
    response = requests.post(f'{backend_url}/insert_review', json=data_dict, timeout=15)
    response.raise_for_status()
    return response.json()
