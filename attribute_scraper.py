import json
import pandas as pd
import requests
import pprint
from utils import Utils

base_url = 'https://mmolb.com/api'
liberty = '6805db0cac48194de3cd3fea'
liberty_league = requests.get(f'https://mmolb.com/api/league/{liberty}').json()
lib_teams = liberty_league['Teams']


def get_league(league: str) -> list:
    # take league ID, return team IDs
    url = f'{base_url}/league/{league}'
    r = requests.get(url).json()
    return r['Teams']

def get_team(team: str) -> list:
    url = f'{base_url}/team/{team}'
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()['Players']
    else:
        print(r)

def get_player_stats(player: str) -> list:
    r = requests.get(f'{base_url}/player/{player}')
    stats_dict = {}
    try:
        stats = r.json()['Talk']
        for k,v in stats.items():
            stars = v['stars']
            stars_to_nums = {attr: len(val) for attr, val in stars.items()}
            stats_dict[k] = stars_to_nums
        print(stats_dict)
        return stats_dict
    except Exception as e:
        print(e)
        print(f'Player ID {player} has no Talk stats.')
        return {}
        
    

def compile_attribute_dict(league):
    league = get_league(league)
    teams = {}
    team_progress = 0
    for team in league:
        teams[team] = [{player['PlayerID']:get_player_stats(player['PlayerID'])} for player in get_team(team)]
        team_progress += 1
        print(f'Loaded {team_progress} out of {len(league)} teams.')
    return teams

def retrieve(league = None):
    if league:
        db = compile_attribute_dict(league)
    
    Utils.write_or_access_json('attributes_db.json',db)

def make_df(data):
    # Step 1: Get full attribute set from first instance of each category
    full_attrs = {}  # e.g., { "Batting": ["Aiming", "Contact", ...], ... }

    for players in data.values():
        for player_entry in players:
            for _, categories in player_entry.items():
                for cat_name, attrs in categories.items():
                    if cat_name not in full_attrs:
                        full_attrs[cat_name] = list(attrs.keys())
            # Break as soon as we’ve found all 4 categories
            if len(full_attrs) == 4:
                break
        if len(full_attrs) == 4:
            break

    # Step 2: Extract data into flat rows
    rows = []

    for team_id, players in data.items():
        for player_entry in players:
            for player_id, categories in player_entry.items():
                row = {"team_id": team_id, "player_id": player_id}
                for cat, attr_list in full_attrs.items():
                    values = categories.get(cat, {})
                    for attr in attr_list:
                        col = f"{attr}"
                        row[col] = values.get(attr)
                rows.append(row)

    return pd.DataFrame(rows)

df = make_df(Utils.access_json('attributes_db.json'))
Utils.write_csv(df,'attributes_db.csv')