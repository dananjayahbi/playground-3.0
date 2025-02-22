import requests

API_URL = "http://127.0.0.1:8000/chat"
response = requests.post(API_URL, json={"message": "Hello!"})
print(response.json())
