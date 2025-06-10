import requests
from utils import Utils

chicken_id = '680e477a7d5b06095ef46ad1'
base_url = 'https://mmolb.com/api/team'

r = requests.get(f'{base_url}/{chicken_id}')

player_index = 9

print(Utils.printout_header(f'{r.json()['Players'][player_index]['FirstName']} {r.json()['Players'][player_index]['LastName']}'))
print(r.json()['Players'][player_index]['Stats'])