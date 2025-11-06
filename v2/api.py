import requests
import requests_cache
import pandas as pd
import psycopg2
from team import Team, LightTeam
from player import Player
from league import League
from io import StringIO
from tqdm import tqdm

class APIHandler:
    def __init__(self,team_id: str ='680e477a7d5b06095ef46ad1',default_season: int = 7) -> None:
        #requests_cache.install_cache("mmolb_http_cache", backend="sqlite", expire_after=None)
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

    def clear_cache():
        requests_cache.clear()

        print('Cache has been cleared.')

    def help(self,attrs: bool = False,methods: bool = False, printout=True) -> list:
        if printout: print('======== API Handler Class Help ========')
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

    def get_team(self,team_id: str = None) -> Team:
        # build the team object
        if not team_id:
            team_id = self.team_id
        r = self.session.get(f'{self.base_url}/team/{team_id}')
        team = Team(r.json(),api_handler=self)
        
        # build the players
        player_ids = [plyr['PlayerID'] for plyr in team.player_data]
        player_objects = []
        for id in tqdm(player_ids,desc='Getting player data'):
            player_objects.append(Player(self.get_player_data(id)))
        
        # insert them into team data
        team.players = player_objects

        self.team_obj = team
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


    def safe_get_player_attr(self, player_name, attr):
        try:
            player = self.team_obj.get_player(player_name)
            return getattr(player, attr, pd.NA)
        except Exception:
            return None

    def get_league(self,league_id: str = None, populate: str = None) -> League: # THIS NEEDS TO BE PAGINATED BEFORE IT WILL WORK
        # take a list and split it into a list of lists w/ max length = page_length
        
        def paginate(id_list: list, page_length: int = 100) -> list:
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
        def batch_teams(page):
            teams_str = ''
            for t in page:
                if t != page[-1]:
                    teams_str += f'{t},'
                else:
                    teams_str += t
            teams_url = f'{self.base_url}/teams?ids={teams_str}'
            r2 = self.session.get(f'{teams_url}')
            return r2

        league_list = []

        # default to API obj default league if not specified
        if league_id is None:
            league_id = self.team_obj.league

        # request league data, come back with a list of team IDs
        r1 = self.session.get(f'{self.base_url}/league/{league_id}').json()
        teams = r1['Teams']

        # paginate the request, roll it together, and build the League object
        teams = paginate(teams)
        for page in teams:
            batch = batch_teams(page).json()
            league_list += batch['teams']
        league = League(r1)
        league.teams = [LightTeam(team_data=td) for td in league_list]

        print(league.teams[0].player_ids)


        try:
            team_to_pop = league.get_team(populate)
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

        elif populate in ['all','All','ALL']: # do the big populate
            for team_obj in tqdm(league.teams,desc='Loading teams'):
                team_to_pop = league.get_team(team_obj.name)
                player_objs = []
                for player_id in tqdm(team_to_pop.player_ids.values(), desc=f'Getting players for {team_to_pop.name}'):
                    player_objs.append(self.get_player_data(player_id))
                team_to_pop.players = player_objs
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