import requests

base_url = 'https://freecashe.ws/team/6805db0cac48194de3cd407c/Records'
base_url = 'https://mmolb.com/api/team/6805db0cac48194de3cd407c'

r = requests.get(base_url)
print(f'====================================\n{base_url}\n====================================')
print(dir(r))
print(r.json())