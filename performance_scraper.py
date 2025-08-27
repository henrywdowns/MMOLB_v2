import typing
import json
import pandas as pd
import requests
import pprint
from utils import Utils

base_url = 'https://mmolb.com/api'
liberty = '6805db0cac48194de3cd3fea'
isosceles = '6805db0cac48194de3cd3fe9'
clean = '6805db0cac48194de3cd3fef'
liberty_league = requests.get(f'https://mmolb.com/api/league/{liberty}').json()
isosceles_league = requests.get(f'https://mmolb.com/api/league/{isosceles}').json()
print(isosceles_league.keys())
print(liberty_league.keys())
lib_teams = liberty_league['Teams']
iso_teams = isosceles_league['Teams']


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
        print(f'Loaded {team_progress} out of {len(league)} teams. {team}')
    print(f'loaded {len(teams.keys())} teams. -- compile_attribute_dict()')
    return teams

def retrieve_and_save(type: str, league: str) -> None:
    if not league:
        raise ValueError("retrieve_and_save requires a league ID.")
    
    new_data = compile_attribute_dict(league, type)
    print(f'New data compiled: {len(new_data.keys())} teams. -- retrieve_and_save()')
    try:
        db = Utils.access_json(f'{type}_db.json')
        print(f'Data found in db for {len(db.keys())} teams.')
        if not isinstance(db, dict):
            db = {}
    except Exception:
        print('No data found in db.')
        db = {}

    # Overwrite the teams we just fetched (latest wins), keep others intact
    db.update(new_data)
    print(f'Database updated. Now contains {len(db.keys())} team records.')

    Utils.write_json(f'{type}_db.json', db)
    print(f'Length of db: {len(db.keys())}')
    print(f'Length of db.json: {len(Utils.access_json(f'{type}_db.json').keys())}')

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
        case 'attributes':
            return make_attr_df(data)
        case 'performance':
            return make_perf_df(data)
    print('Something is wrong!')

def do_the_whole_thing(leagues: typing.List[str]):
    for league in leagues:
        retrieve_and_save('attributes',league)
        retrieve_and_save('performance',league)
        print(f'Finished updating player data for league ID {league}. Writing CSVs...')
        df = make_df(Utils.access_json('attributes_db.json'),'attributes')
        Utils.write_csv(df,'attributes_db.csv')
        df = make_df(Utils.access_json('performance_db.json'),'performance')
        Utils.write_csv(df,'performance_db.csv')

do_the_whole_thing([liberty,clean,isosceles])