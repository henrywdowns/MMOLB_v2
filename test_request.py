import pandas as pd
import requests
from utils import Utils
import pprint
from io import StringIO

chicken_id = '680e477a7d5b06095ef46ad1'
base_url = 'https://mmolb.com/api/'
cashews = 'https://freecashe.ws/'
liberty = '6805db0cac48194de3cd3fea'
rides = '688847f85cb20f9e396df60b'
iso_league = '6805db0cac48194de3cd3fe9'

test_season = '6874db85d759dcb31e10a62a'
test_player = '6841c78e896f631e9d68953c'

r = requests.get(f'{base_url}/team/{chicken_id}')
season = requests.get(f'{base_url}/season/6858e7be2d94a56ec8d460ea')
day = requests.get(f'{base_url}/day/')
game = requests.get(f'{base_url}/watch/')
fc_game = requests.get(f'{cashews}/api/games?season={test_season}&team={chicken_id}')
player = requests.get(f'{base_url}/player/{test_player}') # takes an ID

player_index = 6

def fc_stats(team_id=chicken_id, season:int=5,output:str = 'json') -> str:
    url = "https://freecashe.ws/api/stats"
    params = {
        "season": season,
        "group": "player,team,player_name",
        "team": team_id,
        "fields": "singles,doubles,triples,home_runs,at_bats,walked,hit_by_pitch,plate_appearances,"
                  "stolen_bases,caught_stealing,struck_out,runs,runs_batted_in,sac_flies,groundouts,"
                  "flyouts,popouts,lineouts",
    }
    headers = {
        "Accept": "text/plain; charset=utf-8",
        "Accept-Encoding": "identity",  # disable compression
        "User-Agent": "python-requests",
    }
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    match output:
        case 'text':
            return r.text
        case 'df':
            return pd.read_csv(StringIO(r.text))
        case 'json':
            df = pd.read_csv(StringIO(r.text)).set_index('player_name')
            return df.to_json(orient='index')
    
    print('Something went wrong or output not specified.')

# print(Utils.printout_header(f'{r.json()['Players'][player_index]['FirstName']} {r.json()['Players'][player_index]['LastName']}'))
# print(r.json()['Players'][player_index]['Stats'])


def get_player_in_team(name, printout:bool = True) -> dict:
    #print(r.json()['Players'])
    for player in r.json()['Players']:
        if f'{player['FirstName']} {player['LastName']}' == name:
            player_id = player['PlayerID']
            player_data = requests.get(f'{base_url}/player/{player_id}').json()
            if printout:
                print(player_data)
            return player_data
    print('Name not found. Did you use the full name?')

def get_player(playerid,record=False):
    req = 'playerrecord' if record else 'player'
    r = requests.get(f'{base_url}/{req}/{playerid}').json()
    return r

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

def get_chicken():
    r = requests.get(f'{base_url}/team/{chicken_id}')
    return r.json()

def get_inv():
    r = requests.get(f'{base_url}/inventory/{chicken_id}')
    return r.json()

def get_league(league):
    r = requests.get(f'{base_url}/league/{league}').json()
    return r

def get_team(team: str) -> list:
    url = f'{base_url}/team/{team}'
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()['Players']
    else:
        print(r)


# fc_chicken = fc_stats(output='json')
# print(pd.read_json(fc_chicken))

teams_list = get_league('6805db0cac48194de3cd3fea')['Teams']
# print(teams_list)
print(f'LENGTH: {len(teams_list)} teams.')
teams_str = ''
teams_list = teams_list[:4]
for t in teams_list:
    if t != teams_list[-1]:
        teams_str += f'{t},'
    else:
        teams_str += t

# print(teams_str)

teams_url = f'{base_url}teams?ids={teams_str}'

print('------------- url ------------')
print(teams_url)
print('------------------------------')
teams_r = requests.get(teams_url)
print(teams_r)
pprint.pprint(teams_r.json())

print(get_league('6805db0cac48194de3cd3fea'))