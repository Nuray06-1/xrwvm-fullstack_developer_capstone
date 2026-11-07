import os
from urllib.parse import quote
import requests

BACKEND = os.environ.get('backend_url', 'http://127.0.0.1:3030').rstrip('/')
SENTIMENT = os.environ.get('sentiment_analyzer_url', 'http://127.0.0.1:5050').rstrip('/')

def get_request(endpoint):
    response = requests.get(f'{BACKEND}/{endpoint.lstrip("/")}', timeout=10)
    response.raise_for_status()
    return response.json()

def analyze_review_sentiments(text):
    response = requests.get(f'{SENTIMENT}/analyze/{quote(text, safe="")}', timeout=10)
    response.raise_for_status()
    return response.json()['sentiment']

def post_review(data):
    response = requests.post(f'{BACKEND}/insert_review', json=data, timeout=10)
    response.raise_for_status()
    return response.json()
