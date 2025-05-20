import requests

url = "https://ergon-23o3.onrender.com/api/send_data"
headers = {
    "Authorization": "Bearer supersecret",
    "Content-Type": "application/json"
}
payload = {
    "timestamp": 1234567890,
    "id": 291,
    "data": "11 22 33"
}

res = requests.post(url, json=payload, headers=headers)
print(res.status_code, res.text)
