import requests
import polars as pl
import local_team_data as ltd
import typing
import game_data
from utils import Utils

chicken_id = '680e477a7d5b06095ef46ad1'
lady_beetles = '6805db0cac48194de3cd407c'
base_url = 'https://mmolb.com/api/team'


"""
dict_keys(['Abbreviation', 'Active', 'Augments', 'Championships', 'Color', 'Emoji', 
 'FullLocation', 'League', 'Location', 'Modifications', 'Motto', 'Name', 'OwnerID', 
 'Players', 'Record', 'SeasonRecords', '_id'])

 """
"""
sample of team_data['Players']:

"""

class Team:
    def __init__(self,team_id=chicken_id) -> None:
        self.id = team_id
        self.stored_locally = False
        self.team_stored_data = None
        check_local = self.store_local(get_team_id=team_id)
        if check_local:
            print('Data found in local storage.')
            self.team_data = check_local
            self.stored_locally = True
        else:
            print('No local data found - requesting data from API.')
            self.team_data = requests.get(f'{base_url}/{team_id}').json()
        self.league = self.team_data['League']
        self.modifications = self.team_data['Modifications']
        self.player_data = self.team_data['Players']
        self.players = {}
        for player in self.player_data:
            self.players[player['PlayerID']] = Player(self,player['PlayerID'])
        self.player_names = [player.name for player in self.players.values()]
        #self.player_ids = [player.player_id for player in self.players.values()]
        self.player_ids = {player.name: player.player_id for player in self.players.values()}
        self.name = self.team_data['Name']
        self.owner_id = self.team_data['OwnerID']
        self.team_df = self.make_team_df()
        self.record = self.team_data['Record']
        self.season_records = self.team_data['SeasonRecords']
        self.game_history = None # list of ids
        self.game_log = None # object
        self.performance_categories = {
            'Hitter': ['at_bats', 'home_runs', 'runs_batted_in', 'struck_out', 'walked', 'singles', 'doubles', 'stolen_bases', 'plate_appearances', 'runs'],
            'Pitcher': ['era', 'whip', 'strikeouts', 'walks', 'innings_pitched'],
            'Infield': ['field_out', 'errors', 'double_plays'],
            'Outfield': ['field_out', 'flyouts', 'putouts'],
            'Catcher': ['caught_stealing', 'runners_caught_stealing', 'assists']

}
        if not self.stored_locally:
            print(self.team_data)
            self.store_local(team_object=self)
            self.stored_locally = True
        print(f'Team {self.name} successfully initialized.')

    def get_player(self,name: str = None,id: int = None) -> dict:
        if not name:
            if id:
                for p_id in self.player_data:
                    if id == p_id['PlayerID']:
                        return p_id # this is not just an id, it's a full player dict
                print('Player ID not found in team.')
                return
        elif name:
            for p_name in self.player_data:
                if name == f'{p_name['FirstName']} {p_name['LastName']}':
                    return p_name # this is also the full player dict
            print('Player name not found. Make sure you have included player\'s full name.')
    
    def make_team_df(self) -> dict:
        dfs_dict = {
            'Catcher':[],
            'Outfield':[],
            'Infield':[],
            'Pitcher':[],
            'Hitter':[]
        } # format is {simplified_position:[player_df for simplified_position]}
        for player in self.players.values():
            if player.slot != 'DH':
                dfs_dict[player.simplified_position].append(player.stats_df) # need to set this up to iterate through self.performance_categories.
            #TODO: add Hitter DF independent of DH slot or position
        return dfs_dict

    def scrape_game_ids(self):
        from bs4 import BeautifulSoup
        import json
        import os
        import datetime as dt
        # scraping game ids from freecashews bc mmolb does a poor job of relating game ids to teams
        base_url = 'https://freecashe.ws/games/'

        # checking for the file early so that i can skip the scraping step if the data's relatively fresh
        if os.path.exists('games.json'):
            with open('games.json','r') as f:
                file = json.load(f)
        else:
            file = {}

        latest = file.get('last_update')
        if latest is not None:
            latest_dt = dt.datetime.fromisoformat(latest)
            if dt.datetime.now()-latest_dt < dt.timedelta(hours=24):
                refresh = input('Data less than 24 hours old. Run anyway? y/n\n>')
                while refresh.lower() not in ['y','n']:
                    refresh = input('Data less than 24 hours old. Run anyway? y/n\n>')
                if refresh.lower() == 'n':
                    print('Data not refreshed.')
                    return
                else:
                    print('Refreshing data anyway.')

        r = requests.get(f'{base_url}{self.id}')
        print('parsed')
        soup = BeautifulSoup(r.text,'html.parser')
        # all the links called "watch" link out to the game page on mmolb, so they necessarily have the game id in the dest url
        watch_dest = [
            a["href"] for a in soup.find_all("a", href=True)
            if "/watch/" in a["href"] and "watch" in a.get_text(strip=True).lower()
        ]
        game_ids = [link.split('/')[-1] for link in watch_dest]

        file['last_update'] = dt.datetime.now().isoformat()
        file[self.id] = game_ids

        with open('games.json','w') as f:
            json.dump(file,f,indent=4)
            
    def get_dir(self,builtins: bool = False) -> list:
        result = dir(self)
        if not builtins:
            result[:] = [item for item in result if not item.startswith('__')]
        return result

    def store_local(self,team_object: object = None, get_team_id: bool = None) -> None:
        import json
        filename = 'teams.json'

        def set_local_data_attribute() -> None:
            temp_local_data = ltd.TeamStorage()
            self.team_stored_data = temp_local_data.get_team_data(self.id)
            print(f'Stored data: {self.team_stored_data.keys()}')

        # get_team_id allows for pulling out of local - a little janky, i know
        if get_team_id: # get_team_id should be a literal id
            try:
                with open(filename,'r') as f:
                    data = json.load(f)
                    #set_local_data_attribute()
                    return data[get_team_id]
            except Exception as e:
                print(f'Error: {str(e)}')
                return
        # if get_team_id is None and there's also no team object to speak of, our business is done here
        if not team_object:
            print('No team data found.')
            return
        # otherwise, we locate the file...
        try:
            with open(filename,'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f'No file found: {str(e)}')
            data = {}
        # ...and dump the new json
        with open(filename,'w') as f:
            data[team_object.id] = team_object.team_data
            json.dump(data, f, indent=4)
            print(f'{filename} successfully saved.')  
            #set_local_data_attribute()
    
    def get_game_history(self) -> list:
        game_log = game_data.GameLog(self)
        self.game_log = game_log
        self.game_history = game_log.game_ids

class Player:
    def __init__(self,team_object,player_id) -> None:
        self.player_id = player_id
        self.team = team_object
        self.data = self.team.get_player(id=player_id)
        self.name = f'{self.data['FirstName']} {self.data['LastName']}'
        self.position = self.data['Position']
        self.slot = self.data['Slot']
        self.simplified_position = None
        match self.position:
            case 'C': 
                self.simplified_position = 'Catcher'
            case 'LF'|'CF'|'RF':
                self.simplified_position = 'Outfield'
            case '1B'|'2B'|'3B'|'SS':
                self.simplified_position = 'Infield'
            case 'SP'|'RP'|'CL':
                self.simplified_position = 'Pitcher'
            case _:
                print(f'Need to categorize {self.position}')
        self.stats = self.data['Stats']
        self.stats_df = pl.DataFrame(self.stats)

    def get_dir(self, builtins: bool = False) -> list:
        result = dir(self)
        if not builtins:
            result[:] = [item for item in result if not item.startswith('__')]
        return result
    
    def extract_stats(self) -> dict:
        # simplified positions translate to position-specific KPIs
        # store derived stats in a new file, derived_stats.json
        derived_stats = Utils.access_json('derived_stats.json')

        # calculate appearances/games played. god this was complicated to nail down, but now I have it
        player_appearance_list = Utils.access_json('games.json')['appearances'][self.player_id]
        player_appearances = len(player_appearance_list)
        player_derived_stats = Utils.ensure_nested_dict(derived_stats,self.team.id,self.player_id)# derived_stats[self.team.id][self.player_id]
        player_derived_stats['appearances'] = player_appearances
        
        # everyone bats, but apparently pitchers dont get stats
        if self.simplified_position != 'Pitcher':
            batting = {}
            hits = self.stats['singles'] + self.stats['doubles'] + self.stats['triples'] + self.stats['home_runs']
            batting['hits'] = hits
            batting['batting_avg'] = hits/self.stats['at_bats']
            batting['on_base_percentage'] = (hits + self.stats['walked'] + self.stats['hit_by_pitch'])/self.stats['plate_appearances']
            batting['slugging'] = (self.stats['singles'] + 2*self.stats['doubles'] + 3*self.stats['triples'] + 4*self.stats['home_runs'])/self.stats['at_bats']
            batting['obps'] = batting['on_base_percentage'] + batting['slugging']
            batting['risp_batting_avg'] = (self.stats['singles_risp'] + self.stats['doubles_risp'] + self.stats.get('triples_risp',0) + self.stats['home_runs_risp'])/self.stats['at_bats_risp']
            batting['risp_improvement'] = batting['risp_batting_avg'] - batting['batting_avg']
            batting['risp_diff_percentage'] = batting['risp_improvement']/batting['batting_avg']
            batting['isolated_power'] = batting['slugging'] - batting['batting_avg']
            batting['at_bats_per_appearance'] = self.stats['at_bats']/player_appearances
            
            player_derived_stats['batting'] = batting

        # infielding
        if self.simplified_position == 'Infield':
            infielding = {}
            infielding['putouts_per_game'] = self.stats['putouts']/player_appearances
            infielding['fielding_percentage'] = (self.stats['putouts'] + self.stats['assists'])/(self.stats['putouts'] + self.stats['assists'] + self.stats['errors'])
            infielding['range_factor_per_game'] = (self.stats['putouts'] + self.stats['assists'])/player_appearances
            infielding['fielding_percentage_risp'] = (self.stats['assists_risp'] + self.stats['putouts_risp'])/(self.stats['assists_risp'] + self.stats['putouts_risp'] + self.stats['errors_risp'])
            infielding['fp_risp_improvement'] = infielding['fielding_percentage_risp'] - infielding['fielding_percentage']
            infielding['risp_diff_percentage'] = infielding['fp_risp_improvement']/infielding['fielding_percentage']

            player_derived_stats['infield'] = infielding

        if self.simplified_position == 'Outfield':
            outfielding = {}
            outfielding['putouts_per_game'] = self.stats['putouts']/player_appearances
            outfielding['fielding_percentage'] = (self.stats['putouts'] + self.stats['assists'])/(self.stats['putouts'] + self.stats['assists'] + self.stats['errors'])
            outfielding['range_factor_per_game'] = (self.stats['putouts'] + self.stats['assists'])/player_appearances
            outfielding['fielding_percentage_risp'] = (self.stats['assists_risp'] + self.stats['putouts_risp'])/(self.stats['assists_risp'] + self.stats['putouts_risp'] + self.stats['errors_risp'])
            outfielding['fp_risp_improvement'] = outfielding['fielding_percentage_risp'] - outfielding['fielding_percentage']
            outfielding['risp_diff_percentage'] = outfielding['fp_risp_improvement']/outfielding['fielding_percentage']

            player_derived_stats['outfield'] = outfielding

        if self.simplified_position == 'Catcher':
            catching = {}
            catching['putouts_per_game'] = self.stats['putouts']/player_appearances
            catching['fielding_percentage'] = (self.stats['putouts'] + self.stats['assists'])/(self.stats['putouts'] + self.stats['assists'] + self.stats['errors'])
            catching['range_factor_per_game'] = (self.stats['putouts'] + self.stats['assists'])/player_appearances
            catching['fielding_percentage_risp'] = (self.stats['assists_risp'] + self.stats['putouts_risp'])/(self.stats['assists_risp'] + self.stats['putouts_risp'] + self.stats['errors_risp'])
            catching['fp_risp_improvement'] = catching['fielding_percentage_risp'] - catching['fielding_percentage']
            catching['risp_diff_percentage'] = catching['fp_risp_improvement']/catching['fielding_percentage']

            player_derived_stats['outfield'] = catching
        
        if self.simplified_position == 'Pitcher':
            pitching = {}
            pitching['batters_faced_per_appearance'] = self.stats['batters_faced']/self.stats['appearances']
            pitching['pitches_per_appearance'] = self.stats['pitches_thrown']/self.stats['appearances']
            pitching['innings_pitched'] = self.stats['outs']/3
            pitching['innings_pitched_per_appearance'] = pitching['innings_pitched']/self.stats['appearances']
            pitching['batters_faced_per_inning'] = pitching['batters_faced_per_appearance']/pitching['innings_pitched_per_appearance']
            pitching['strikeout_rate'] = self.stats['strikeouts']/self.stats['batters_faced']
            pitching['ERA'] = (self.stats['earned_runs'] * 9)/pitching['innings_pitched']
            pitching['walks_hits_per_inning_pitched'] = (self.stats['walks'] + self.stats['hits_allowed'])/pitching['innings_pitched']
            pitching['strikeouts_per_nine'] = (self.stats['strikeouts'] * 9)/pitching['innings_pitched']
            pitching['walks_per_nine'] = (self.stats['walks'] * 9)/pitching['innings_pitched']
            pitching['home_runs_allowed_per_nine'] = (self.stats['home_runs_allowed'] * 9)/pitching['innings_pitched']
            pitching['hits_allowed_per_nine'] = (self.stats['hits_allowed'] * 9)/pitching['innings_pitched']
            pitching['strikeouts_to_balls_on_base'] = self.sats['strikeouts']/self.stats['walks']
            pitching['win_rate'] = self.stats['wins']/self.stats['appearances']
            pitching['win_chance_improvement'] = pitching['win_rate']/(self.team.record['Wins']/(self.team.record['Wins']+self.team.record['Losses']))

            player_derived_stats['pitcher'] = pitching

        Utils.write_json('derived_stats.json', derived_stats)


if __name__ == '__main__':
    beetles = Team(lady_beetles)
    #print(beetles.team_data)
