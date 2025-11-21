import requests_cache
import pandas as pd
import psycopg2
from .team import Team, LightTeam
from .player import Player
from .league import League
from .interleague import Interleague
from io import StringIO
from tqdm import tqdm
import datetime as dt

class APIHandler:
    def __init__(self,team_id: str ='680e477a7d5b06095ef46ad1',default_season: int = 7, debug: bool = True) -> None:
        self.debug = debug
        if self.debug:
            self.init_start = dt.datetime.now()
            print(f'APIHandler initialization began at {self.init_start}')
        self.session = requests_cache.CachedSession(
            ".cache/mmolb_http_cache",
            backend="sqlite",
            expire_after=None,          # persist indefinitely unless you clear
            allowable_codes=(200, 204, 404, 500),  # cache “empty”/not-found responses too
            cache_control=False,        # don’t let server disable caching
            stale_if_error=True,        # serve cached value if upstream blips
        )
        self.base_url = r'https://mmolb.com/api'
        self.cashews = r'https://freecashe.ws/'
        self.team = r'team'
        self.teams = r'teams'
        self.player = r'player'
        self.default_season = default_season
        self.team_id = team_id
        self.team_obj = self.get_team(team_id)


    def clear_cache(self):
        self.session.cache.clear()
        print('Cache has been cleared.')

    def help(self,attrs: bool = False,methods: bool = False, printout=True) -> list:
        if printout: print(f'======== {self.__class__.__name__} Class Help ========')
        _attrs = [k for k in self.__dict__.keys()]
        _methods = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
        attrs_methods = [_attrs,_methods]
        if attrs: attrs_methods = _attrs
        elif methods: attrs_methods = _methods
        if printout: print(attrs_methods)
        return attrs_methods

    def get_player_data(self,id) -> dict:
        r = self.session.get(f'{self.base_url}/player/{id}')
        try:
            return r.json()
        except Exception as e:
            if id == None:
                if r == 500:
                    self.session.cache.save_response(r)
            else:
                raise KeyError

    def get_team(self,team_id: str = None, just_checking:bool = False) -> Team:
        # build the team object
        if not team_id:
            team_id = self.team_id
        r = self.session.get(f'{self.base_url}/team/{team_id}')
        team = Team(r.json(),api_handler=self)
        
        # build the players
        player_ids = [plyr['PlayerID'] for plyr in team.player_data]
        player_objects = []
        
        if not just_checking:
            for id in tqdm(player_ids,desc='Getting player data'):
                player_objects.append(Player(self.get_player_data(id)))
        else:
            for id in player_ids:
                player_objects.append(Player(self.get_player_data(id)))
        
        # insert them into team data
        team.players = player_objects
        team.attributes = team.get_attributes()

        self.team_obj = team
        return team

    def get_all_leagues(self,scope='lesser', lesser_sample_size=16) -> Interleague:
        league_ids = {
            "GreaterLeagues": [
                "6805db0cac48194de3cd3fe4",
                "6805db0cac48194de3cd3fe5"
            ],
            "LesserLeagues": [
                "6805db0cac48194de3cd3fe7",
                "6805db0cac48194de3cd3fe8",
                "6805db0cac48194de3cd3fe9",
                "6805db0cac48194de3cd3fea",
                "6805db0cac48194de3cd3feb",
                "6805db0cac48194de3cd3fec",
                "6805db0cac48194de3cd3fed",
                "6805db0cac48194de3cd3fee",
                "6805db0cac48194de3cd3fef",
                "6805db0cac48194de3cd3ff0",
                "6805db0cac48194de3cd3ff1",
                "6805db0cac48194de3cd3ff2",
                "6805db0cac48194de3cd3ff3",
                "6805db0cac48194de3cd3ff4",
                "6805db0cac48194de3cd3ff5",
                "6805db0cac48194de3cd3ff6"
            ]
        }
        league_objs = {
            'lesser': [],
            'greater': []
        }

        if lesser_sample_size < 16:
            import random
            league_ids['LesserLeagues'] = random.sample(league_ids['LesserLeagues'],lesser_sample_size)
            print(f'Sample of {lesser_sample_size} taken from lesser league. Pulling {len(league_ids['LesserLeagues'])} leagues.')

        if scope in ('lesser','both'):
            for league in tqdm(league_ids["LesserLeagues"],desc=f'Loading Lesser Leagues...'):
                league_objs['lesser'].append(self.get_league(league,populate='all'))
        if scope in ('greater','both'):
            for league in tqdm(league_ids["GreaterLeagues"],desc=f'Loading Greater Leagues...'):
                league_objs['greater'].append(self.get_league(league,populate='all'))

        if scope not in ('lesser', 'greater', 'both'):
            raise ValueError('InterLeague scope must be "lesser", "greater", or "both".')


        il = Interleague(lesser_leagues=league_objs["lesser"],greater_leagues=league_objs['greater'],debug=self.debug)
        if self.debug:
            print(f'Interleague object created and initialized. Elapsed time: {dt.datetime.now() - self.init_start}')
        return il

    # this db is really granular and complex and i'd rather avoid using if possible. way too much work.
    def connect_beiju(self) -> None:
        return psycopg2.connect(
            host='mmoldb.beiju.me',
            port=42416,
            dbname='mmoldb',
            user='guest',
            password='moldybees'
        )
    # idea here is to have a folder of sql queries that i can draw upon to keep it clean, but we will see if i ever finish with this. 
    def beiju_team_stats(self, season: int = None) -> pd.DataFrame:
        if not season:
            season = self.default_season
        conn = self.connect_beiju()
        with open('v2/beiju_sql/player_stats.txt','r') as f:
            sql = f.read()
        df = pd.read_sql(sql, conn, params={"team_id": self.team_id, "season": season})
        conn.close()
        return df

    def batch_players(self, player_ids: list = None, debug=False) -> dict:  
        players_list = []
        if all(players_list) == None:
            return None   
        for page in self.paginate(player_ids):
            players_str = ''
            for p in page:
                if p != None:
                    if p != page[-1]:
                        players_str += f'{p},'
                    else:
                        players_str += p
                else:
                    pass
            players_url = f'{self.base_url}/players?ids={players_str}'
            batch = self.session.get(f'{players_url}').json()
            try:
                players_list += batch['players']
            except Exception as e:
                if debug:
                    print(e)
                else:
                    pass
        return players_list

    def safe_get_player_attr(self, player_name, attr):
        try:
            player = self.team_obj.get_player(player_name)
            return getattr(player, attr, pd.NA)
        except Exception:
            return None

    def paginate(self,id_list: list, page_length: int = 100) -> list:
            page_list = []
            sub_list = []

            for item in id_list:
                if len(sub_list) >= page_length:
                    page_list.append(sub_list)
                    sub_list = []
                sub_list.append(item)
            if len(sub_list) > 0: # dont want to append [] if sub_list is somehow empty
                page_list.append(sub_list)
            return page_list
        
    # concat ids w/ comma delimiter, compile proper batch api call, build LightTeam object for each
    def batch_teams(self, team_ids_list: list):
        league_list = []
        for page in self.paginate(team_ids_list):
            teams_str = ''
            for t in page:
                if t != page[-1]:
                    teams_str += f'{t},'
                else:
                    teams_str += t
            teams_url = f'{self.base_url}/teams?ids={teams_str}'
            batch = self.session.get(f'{teams_url}').json()
            league_list += batch['teams']
        return league_list

    def get_league(self,league_id: str = None, populate: str = None) -> League: # THIS NEEDS TO BE PAGINATED BEFORE IT WILL WORK
        # default to API obj default league if not specified
        if league_id is None:
            league_id = self.team_obj.league

        # request league data, come back with a list of team IDs
        r1 = self.session.get(f'{self.base_url}/league/{league_id}').json()
        teams = r1['Teams']

        # run the batch teams api call and build the League object
        league_list = self.batch_teams(teams)
        league = League(r1)
        league.teams = [LightTeam(team_data=td,api_handler=self) for td in league_list]
        league.__setattr__('_populate_status',populate)
        # teams are found and now i need to populate the teams with players. TODO: replace this nonsense with batch players pull
        try:
            team_to_pop = league.get_team(populate,just_checking=True)
        except:
            team_to_pop = False

        # building the players can be expensive, so optionally populate them. 
        if populate is None:
                pass
        elif team_to_pop != False: # if the team can be searched, it exists. populate just that.
            player_objs = []
            for player_id in tqdm(team_to_pop.player_ids.values(), desc=f'Getting players for {team_to_pop.name}'):
                player_objs.append(self.get_player_data(player_id))
            team_to_pop.players = player_objs
            team_to_pop.attributes = team_to_pop.get_attributes()

        elif populate in ['all','All','ALL']: # do the big populate
            for team_obj in tqdm(league.teams,desc='      Loading teams'):
                team_to_pop = league.get_team(team_obj.name)
                player_ids_list = []
                for player_id in team_to_pop.player_ids.values():
                    player_ids_list.append(player_id)
                player_objs = self.batch_players(player_ids_list)
                team_to_pop.players = player_objs
                team_to_pop.attributes = team_to_pop.get_attributes()
            setattr(league,'names_by_id',{t._id:t.name for t in league.teams})
        else:
            raise ValueError('"Populate" keyword must be "all", a team name, a team ID, or None.')
        return league


    # attempting to get derived stats from freecashe.ws so i dont have to calculate them myself
    def fc_team_stats(self, season: int = None, team_id: str = None, stats_type: str = None) -> pd.DataFrame:
        season = season or self.default_season
        team_id = team_id or self.team_id

        match stats_type:
            case "batting"|"hitting":
                fields = ("singles,doubles,triples,home_runs,at_bats,walked,hit_by_pitch,"
                        "plate_appearances,stolen_bases,caught_stealing,struck_out,runs,"
                        "runs_batted_in,sac_flies,groundouts,flyouts,popouts,lineouts")
            case "pitching":
                fields = ("outs,earned_runs,home_runs_allowed,walks,hit_batters,strikeouts,"
                        "hits_allowed,wins,losses,saves,blown_saves,unearned_runs,appearances,starts")
            case _:
                raise ValueError("stats_type must be 'batting' or 'pitching'")

        r = self.session.get(
            "https://freecashe.ws/api/stats",
            params={
                "season": season,
                "group": "player,team,player_name",
                "team": team_id,
                "fields": fields,
            },
            timeout=20,
        )
        # Fail loudly if 4xx/5xx instead of silently returning None
        r.raise_for_status()

        team_df = pd.read_csv(StringIO(r.text))
        team_df['positiontype'] = team_df["player_name"].apply(lambda n: self.safe_get_player_attr(n, "positiontype"))

        return team_df
    
    def fc_league_stats(self, season: int = None, league_id: str = None, stats_type: str = None) -> pd.DataFrame:
        season = season or self.default_season
        league_id = league_id or self.team_obj.league

        match stats_type:
            case "batting" | "hitting":
                fields = ("singles,doubles,triples,home_runs,at_bats,walked,hit_by_pitch,"
                        "plate_appearances,stolen_bases,caught_stealing,struck_out,runs,"
                        "runs_batted_in,sac_flies,groundouts,flyouts,popouts,lineouts")
            case "pitching":
                fields = ("outs,earned_runs,home_runs_allowed,walks,hit_batters,strikeouts,"
                        "hits_allowed,wins,losses,saves,blown_saves,unearned_runs,appearances,starts")
            case _:
                raise ValueError("stats_type must be 'batting' or 'pitching'")

        r = self.session.get(
            "https://freecashe.ws/api/stats",
            params={
                "season": season,
                "group": "player,team,player_name",
                "league": league_id,
                "fields": fields,
            },
            timeout=20,
        )
        r.raise_for_status()

        league_df = pd.read_csv(StringIO(r.text))
        league_df['positiontype'] = league_df["player_name"].apply(lambda n: self.safe_get_player_attr(n, "positiontype"))

        return league_df