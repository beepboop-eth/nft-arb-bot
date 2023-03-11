import requests

url = 'https://ethgasstation.info/api/ethgasAPI.json'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
    print('Safe Gas Price:', data['safeLow'])
    print('Standard Gas Price:', data['average'])
    print('Fast Gas Price:', data['fast'])
else:
    print('Failed to retrieve gas prices:', response.status_code)