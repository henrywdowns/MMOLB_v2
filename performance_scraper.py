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

def get_player_stats(player: str,type: str = None) -> list:
    if player == '#':
        return {}
    r = requests.get(f'{base_url}/player/{player}')
    if not r.json().get('Stats'):
        return {}
    stats_dict = {}
    if type == 'attributes':
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
    elif type == 'performance':
        try:
            stats_dict = list(r.json()['Stats'].values())[0]
            return(stats_dict)
        except Exception as e:
            print(e)
            return {}


def compile_attribute_dict(league: str,type:str) -> dict:
    league = get_league(league)
    teams = {}
    team_progress = 0
    for team in league:
        teams[team] = [{player['PlayerID']:get_player_stats(player['PlayerID'],type)} for player in get_team(team)]
        team_progress += 1
        print(f'Loaded {team_progress} out of {len(league)} teams.')
    return teams

def retrieve_and_save(type: str, league: str = None) -> None:
    if league:
        db = compile_attribute_dict(league, type)
    
    Utils.write_or_access_json(f'{type}_db.json',db)

def make_attr_df(data: dict) -> pd.DataFrame:
    full_attrs = {}

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

def make_perf_df(data: dict) -> pd.DataFrame:
    rows = []
    for outer_id, stat_list in data.items():
        for item in stat_list:
            for inner_id, metrics in item.items():
                flat_row = {"outer_id": outer_id, "inner_id": inner_id}
                flat_row.update(metrics)
                rows.append(flat_row)

    df = pd.DataFrame(rows)
    return df

def make_df(data: dict, type: str) -> pd.DataFrame:
    match type:
        case 'attribute':
            return make_attr_df(data)
        case 'performance':
            return make_perf_df(data)
    print('Something is wrong!')

df = make_df(Utils.access_json('performance_db.json'),'performance')
Utils.write_csv(df,'performance_db.csv')

#retrieve_and_save('performance',liberty)