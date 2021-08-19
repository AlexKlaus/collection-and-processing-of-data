import requests
import json

user = 'AlexKlaus'
response = requests.get(f'https://api.github.com/users/{user}/repos')
result = json.loads(response.text)

with open('task_1.json', 'w') as f:
    json.dump(result, f)


for repo in result:
    print(repo['name'])
