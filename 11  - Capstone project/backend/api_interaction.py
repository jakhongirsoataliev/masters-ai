import requests

# Example of interacting with a third-party API
def send_data_to_api(url, data):
    response = requests.post(url, json=data)
    return response.status_code, response.json()

def fetch_data_from_api(url):
    response = requests.get(url)
    return response.status_code, response.json()