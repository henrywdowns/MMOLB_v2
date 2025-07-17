import requests
from utils import Utils

chicken_id = '680e477a7d5b06095ef46ad1'
base_url = 'https://mmolb.com/api/'
cashews = 'https://freecashe.ws/'

test_season = '6874db85d759dcb31e10a62a'

r = requests.get(f'{base_url}/team/{chicken_id}')
season = requests.get(f'{base_url}/season/6858e7be2d94a56ec8d460ea')
day = requests.get(f'{base_url}/day/')
game = requests.get(f'{base_url}/watch/')
fc_game = requests.get(f'{cashews}/api/games?season={test_season}&team={chicken_id}')

player_index = 6

# print(Utils.printout_header(f'{r.json()['Players'][player_index]['FirstName']} {r.json()['Players'][player_index]['LastName']}'))
# print(r.json()['Players'][player_index]['Stats'])


def get_player(name):
    print(r.json()['Players'])
    for player in r.json()['Players']:
        if player['FirstName'] == name:
            print(player)

def get_season(season):
    s = requests.get(f'{base_url}/season/{season}')
    return s.json()

def get_options():
    print(r.json().keys())

def cashews_get_game(game_id):
    g = requests.get(f'{cashews}{game_id}').json()
    return g

def get_day(day_id, team_id = chicken_id):
    d = dict(requests.get(f'{base_url}/day/{day_id}').json())
    team_day = {
        'Day': d['Day'],
        'Game': d['Games']
        }
    for item in team_day['Game']:
        if item['AwayTeamID'] == team_id or item['HomeTeamID'] == team_id:
            team_day['Game'] = item
            return team_day

#print(season.json())

# Utils.write_json()

# print(game.json())

#print(r.json().keys())
#print(r.json()['SeasonRecords'])
#print(get_season('6874db85d759dcb31e10a62a'))
#print(get_day('6874db84d759dcb31e10a53b'))
#print(cashews_get_game('6874e3b1d759dcb31e10a64e'))
game_id = '6874db84d759dcb31e10a53a'
game_attempt = requests.get(f'https://mmolb.com/schedule/{game_id}')
print(game_attempt.text)

print(requests.get('https://mmolb.com/api/game/687561c56154982c31f5cc7c').json())