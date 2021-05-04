import requests

headers = {
    'Accept': 'application/vnd.heroku+json; version=3',
    'Authorization': 'Basic 1ec0d46f-70f0-486f-b853-62e4bc564b36',
    'Content-Type': 'application/json',
}

data = {
    'description': 'sample',
}

url = 'https://api.heroku.com/oauth/authorization'

response = requests.post(url=url, headers=headers, json=data)
try:
    print(response.json())
except:
    print(response.content)