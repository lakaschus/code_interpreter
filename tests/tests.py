import requests

url = "http://localhost:5005/code"
example = open("code.txt", "r").read()
data = {"code": example}
response = requests.post(url, json=data)
print(response.json())
