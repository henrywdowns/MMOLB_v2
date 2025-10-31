import requests, pprint
import pandas as pd
import psycopg2

class APIHandler:
    def __init__(self,team_id: str ='680e477a7d5b06095ef46ad1',default_season: int = 7) -> None:
        self.base_url = r'https://mmolb.com/api/'
        self.cashews = r'https://freecashe.ws/'
        self.team = r'team'
        self.teams = r'teams'
        self.player = r'player'
        self.team_id = team_id
        self.default_season = default_season

    def help(self,attrs: bool = False,methods: bool = False, printout=True):
        if printout: print('======== API Handler Class Help ========')
        _attrs = [k for k in self.__dict__.keys()]
        _methods = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
        attrs_methods = [_attrs,_methods]
        if attrs: attrs_methods = _attrs
        elif methods: attrs_methods = _methods
        if printout: print(attrs_methods)
        return attrs_methods

    def get_team(self,team_id: str = None) -> dict:
        if not team_id:
            team_id = self.team_id
        r = requests.get(f'{self.base_url+self.team}/{team_id}')
        team = Team(r.json())
        return team
    
    # this db is really granular and complex and i'd rather avoid using if possible. way too much work.
    def connect_beiju(self) -> None:
        return psycopg2.connect(
            host='mmoldb.beiju.me',
            port=42416,
            dbname='mmoldb',
            user='guest',
            password='moldybees'
        )
    
    def beiju_team_stats(self, season: int = None) -> pd.DataFrame:
        if not season:
            season = self.default_season
        conn = self.connect_beiju()
        with open('v2/beiju_sql/player_stats.txt','r') as f:
            sql = f.read()
        df = pd.read_sql(sql, conn, params={"team_id": self.team_id, "season": season})
        conn.close()
        return df

    def fc_team_stats(self, season: int = None) -> dict:
        import json
        if not season:
            season = self.default_season
        # https://freecashe.ws/team/680e477a7d5b06095ef46ad1/stats
        # r = requests.get(f'{self.cashews}/team/{self.team_id}/stats')

        r = requests.get(f'https://freecashe.ws/api/stats?season={season}&group=player%2Cteam%2Cplayer_name&league=6805db0cac48194de3cd3fea&fields=singles%2Cdoubles%2Ctriples%2Chome_runs%2Cat_bats%2Cwalked%2Chit_by_pitch%2Cplate_appearances%2Cstolen_bases%2Ccaught_stealing%2Cstruck_out%2Cruns%2Cruns_batted_in%2Csac_flies%2Cgroundouts%2Cflyouts%2Cpopouts%2Clineouts')
        
        # j = json.loads(r.text) # returns a text-formatted json and must be converted
        return r
class Team:
    def __init__(self,team_data: dict) -> None:
        self._team_data = team_data
        for k, v in self._team_data.items(): # unpack self._team_data json response and assign as attributes
            setattr(self, k.lower(), v)
        self.player_data = self.players
        self.players = self._build_players()

    def help(self,attrs: bool = False,methods: bool = False, printout = True):
        if printout: print('======== Team Class Help ========')
        _attrs = [k for k in self.__dict__.keys()]
        _methods = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
        attrs_methods = [_attrs,_methods]
        if attrs: attrs_methods = _attrs
        elif methods: attrs_methods = _methods
        if printout: print(attrs_methods)
        return attrs_methods
    
    def _build_players(self):
        player_ids = [plyr['PlayerID'] for plyr in self.player_data]
        player_objects = []
        for id in player_ids:
            player_objects.append(Player(id))
        
        return player_objects
        # for a in player_objects[-1].help(attrs=True):
        #     print(f'==========={a}============')
        #     print(getattr(player_objects[-1],a))

    def get_player(self, key: str):
        import re
        if re.search(r"\d", key):
            _players_by_id = {ply.id: ply for ply in self.players}
            return _players_by_id[key]
        else:
            _players_by_name = {ply.full_name: ply for ply in self.players}
            return _players_by_name[key]
        
    def get_roster(self,roster_type: str = None) -> dict:
        t = self._team_data
        roster = {
            "Players": t.get("Players"),
            "Bench": t.get("Bench")
        }
        if roster_type:
            roster_type = roster_type.capitalize()
            roster = {roster_type: roster.get(roster_type)}
        return roster
    

class Player:
    def __init__(self, player_id: str) -> None:
        
        self.id = player_id
        self.base_url = r'https://mmolb.com/api/player'
        self._data = dict(self._get_player_data())
        for k, v in self._data.items(): # unpack self._data json response and assign as attributes
            setattr(self, k.lower(), v)
        self.full_name = f'{self._data['FirstName']} {self._data['LastName']}'
        self.attributes = self._get_attributes()
    
    def help(self,attrs: bool = False,methods: bool = False, printout = True):
        if printout: print('======== Player Class Help ========')
        _attrs = [k for k in self.__dict__.keys()]
        _methods = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
        attrs_methods = [_attrs,_methods]
        if attrs: attrs_methods = _attrs
        elif methods: attrs_methods = _methods
        if printout: print(attrs_methods)
        return attrs_methods

    def _get_player_data(self):
        r = requests.get(f'{self.base_url}/{self.id}')
        return r.json()
    
    def _get_attributes(self):
        attrs = self._data['Talk']
        attrs_dict = {
            'total_attr_dict': {k.capitalize(): {} for k in attrs.keys()},
            'base_attr_dict': {k.capitalize(): {} for k in attrs.keys()},
            'equip_attr_dict': {k.capitalize(): {} for k in attrs.keys()}
        }

        for cat in attrs.keys():
            stars = attrs[cat]['stars']
            attrs_dict['total_attr_dict'][cat] = {k: v['total'] for k, v in stars.items()}
            attrs_dict['base_attr_dict'][cat] = {k: v['base_total'] for k, v in stars.items()}
            attrs_dict['equip_attr_dict'][cat] = {k:round(v['total']-v['base_total'],2) for k, v in stars.items()}

        return attrs_dict

import requests, pprint
import pandas as pd
import psycopg2

class APIHandler:
    def __init__(self,team_id: str ='680e477a7d5b06095ef46ad1',default_season: int = 7) -> None:
        self.base_url = r'https://mmolb.com/api/'
        self.cashews = r'https://freecashe.ws/'
        self.team = r'team'
        self.teams = r'teams'
        self.player = r'player'
        self.team_id = team_id
        self.default_season = default_season

    def help(self,attrs: bool = False,methods: bool = False, printout=True):
        if printout: print('======== API Handler Class Help ========')
        _attrs = [k for k in self.__dict__.keys()]
        _methods = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
        attrs_methods = [_attrs,_methods]
        if attrs: attrs_methods = _attrs
        elif methods: attrs_methods = _methods
        if printout: print(attrs_methods)
        return attrs_methods

    def get_team(self,team_id: str = None) -> dict:
        if not team_id:
            team_id = self.team_id
        r = requests.get(f'{self.base_url+self.team}/{team_id}')
        team = Team(r.json())
        return team
    
    # this db is really granular and complex and i'd rather avoid using if possible. way too much work.
    def connect_beiju(self) -> None:
        return psycopg2.connect(
            host='mmoldb.beiju.me',
            port=42416,
            dbname='mmoldb',
            user='guest',
            password='moldybees'
        )
    
    def beiju_team_stats(self, season: int = None) -> pd.DataFrame:
        if not season:
            season = self.default_season
        conn = self.connect_beiju()
        with open('v2/beiju_sql/player_stats.txt','r') as f:
            sql = f.read()
        df = pd.read_sql(sql, conn, params={"team_id": self.team_id, "season": season})
        conn.close()
        return df

    def fc_team_stats(self, season: int = None) -> dict:
        import json
        if not season:
            season = self.default_season
        # https://freecashe.ws/team/680e477a7d5b06095ef46ad1/stats
        # r = requests.get(f'{self.cashews}/team/{self.team_id}/stats')

        r = requests.get(f'https://freecashe.ws/api/stats?season={season}&group=player%2Cteam%2Cplayer_name&league=6805db0cac48194de3cd3fea&fields=singles%2Cdoubles%2Ctriples%2Chome_runs%2Cat_bats%2Cwalked%2Chit_by_pitch%2Cplate_appearances%2Cstolen_bases%2Ccaught_stealing%2Cstruck_out%2Cruns%2Cruns_batted_in%2Csac_flies%2Cgroundouts%2Cflyouts%2Cpopouts%2Clineouts')
        
        # j = json.loads(r.text) # returns a text-formatted json and must be converted
        return r