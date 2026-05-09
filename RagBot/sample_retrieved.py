import requests

url = "http://api.hooshyar.systemgroup.net/open-router-reverse/v1"

headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek/deepseek-v4-pro",
    "messages": [
        {"role": "user", "content": "Hello! Write a short poem about AI."}
    ]
}

response = requests.post(url, headers=headers, json=data)
import pdb

pdb.set_trace()
print(response.json())
