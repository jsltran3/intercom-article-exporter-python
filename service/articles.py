import requests

url = "https://api.intercom.io/articles"

headers = {
  "Intercom-Version": "2.10",
  "Authorization": "Bearer <YOUR_TOKEN_HERE>"
}

response = requests.get(url, headers=headers)

data = response.json()
print(data)