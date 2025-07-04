import requests
from utils import Utils

chicken_id = '680e477a7d5b06095ef46ad1'
base_url = 'https://mmolb.com/api/'

r = requests.get(f'{base_url}/team/{chicken_id}')
season = requests.get(f'{base_url}/season/6858e7be2d94a56ec8d460ea')
day = requests.get(f'{base_url}/day/1')

player_index = 6

# print(Utils.printout_header(f'{r.json()['Players'][player_index]['FirstName']} {r.json()['Players'][player_index]['LastName']}'))
# print(r.json()['Players'][player_index]['Stats'])


def get_player(name):
    print(r.json()['Players'])
    for player in r.json()['Players']:
        if player['FirstName'] == name:
            print(player)

def get_options():
    print(r.json().keys())

# print(season.json())

print(r.json()['SeasonRecords'])

Utils.write_json()