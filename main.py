import requests
import json
from translate import Translator

headers = {
    'Content-Type': 'application/json',
	'charset': 'utf-8'
}

data = '{   "model": "llama3.2",   "prompt":"Who are you"  }'

responses = []

response = requests.post('http://172.17.0.2:11434/api/generate', data=data, )

print(f'response STATUS CODE {response.status_code}')

for line in response.iter_lines():
	response_json = json.loads(line)
	try:
		responses.append(response_json["response"])
	except:
		pass

output = ''

for word in responses:
	output += word

translator = Translator(from_lang="en", to_lang="ru")
output = translator.translate(output)
print(output)