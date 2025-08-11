import datetime as dt
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
        if check_local and (dt.datetime.now() - check_local.get('timestamp') < dt.timedelta(hours=3)):
            print('Data found in local storage.')
            self.team_data = check_local
            self.stored_locally = True
        else:
            print('No recent local data found - requesting data from API.')
            self.team_data = requests.get(f'{base_url}/{team_id}').json()
            # teams_json = Utils.access_json('teams.json')
            # teams_json['self.id'] = self.team_data
        self.league = self.team_data['League']
        try:
            self.record = self.team_data['Record']['Regular Season']
        except:
            self.record = self.team_data['Record']
        self.win_rate = round(self.record['Wins']/(self.record['Wins']+self.record['Losses']),2)
        self.modifications = self.team_data['Modifications']
        self.player_data = self.team_data['Players']
        self.players = {}
        for player in self.player_data:
            self.players[player['PlayerID']] = Player(self,player['PlayerID'])
        self.player_names = [player.name for player in self.players.values()]
        #self.player_ids = [player.player_id for player in self.players.values()]
        self.player_ids = {player.name: player.player_id for player in self.players.values()}
        self.name = self.team_data['Name']
        #self.owner_id = self.team_data['OwnerID']
        self.team_df = self.make_team_df()
        self.season_records = self.team_data['SeasonRecords']
        self.game_history = self.scrape_game_ids(init=True) # list of ids
        self.game_log = None # object
        self.performance_categories = {
            'Hitter': ['at_bats', 'home_runs', 'runs_batted_in', 'struck_out', 'walked', 'singles', 'doubles', 'stolen_bases', 'plate_appearances', 'runs'],
            'Pitcher': ['era', 'whip', 'strikeouts', 'walks', 'innings_pitched'],
            'Infield': ['field_out', 'errors', 'double_plays'],
            'Outfield': ['field_out', 'flyouts', 'putouts'],
            'Catcher': ['caught_stealing', 'runners_caught_stealing', 'assists']

}
        if not self.stored_locally:
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

    def scrape_game_ids(self, init: bool = False):
        from bs4 import BeautifulSoup
        import json
        import os
        import datetime as dt
        # scraping game ids from freecashews bc mmolb does a poor job of relating game ids to teams
        base_url = 'https://freecashe.ws/team/'

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
                if init:
                    print('Init data less than 24 hours old: skipping game scraping. Run Team.scrape_game_ids() manually to refresh.')
                    return
                refresh = input('Data less than 24 hours old. Run anyway? y/n\n>')
                while refresh.lower() not in ['y','n']:
                    refresh = input('Data less than 24 hours old. Run anyway? y/n\n>')
                if refresh.lower() == 'n':
                    print('Data not refreshed.')
                    return
                else:
                    print('Refreshing data anyway.')
        team_stats_url = f'{base_url}{self.id}/stats'
        print(f'Requesting {team_stats_url}')
        r = requests.get(team_stats_url)
        print(f'{r.status_code} Parsed')
        soup = BeautifulSoup(r.text,'html.parser')
        # all the links called "watch" link out to the game page on mmolb, so they necessarily have the game id in the dest url
        watch_dest = [
            a["href"] for a in soup.find_all("a", href=True)
            if "/watch/" in a["href"] and "watch" in a.get_text(strip=True).lower()
        ]
        game_ids = [link.split('/')[-1] for link in watch_dest]
        print(f'Game ids: {game_ids}')

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
        import datetime as dt
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
                    data[get_team_id]['timestamp'] = dt.datetime.now()
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
        data[self.id] = {}
        data[self.id]['timestamp'] = dt.datetime.now()
        with open(filename,'w') as f:
            data[team_object.id] = team_object.team_data
            json.dump(data, f, indent=4)
            print(f'{filename} successfully saved.')  
            #set_local_data_attribute()
    
    def get_game_history(self) -> list:
        game_log = game_data.GameLog(self)
        self.game_log = game_log
        self.game_history = game_log.game_ids

    def get_stats_df(self,cache=False) -> pl.DataFrame:
        stats_dict: dict[str, dict[str, dict[str, any]]] = {}
        for player in self.players.values():
            stats_dict.setdefault(player.simplified_position, {})[player.name] = player.stats
            stats_dict[player.simplified_position][player.name]['detailed_position'] = player.position

        rows = []
        for position, by_name in stats_dict.items():
            for name, stats in by_name.items():
                row = {
                    "position": position,
                    "player": name,
                    **stats,
                }
                rows.append(row)
        final_data = pl.DataFrame(rows)
        if cache:
            Utils.write_csv(final_data,team_name=self.name)
        return final_data

    def get_position_df(self, position: str = 'all') -> pl.DataFrame:
        chk_df = self.get_stats_df()
            
        chk_field = chk_df.filter(
            (pl.col('position') == 'Infield') | (pl.col('position') == 'Outfield') | (pl.col('position') == 'Catcher')
        ).select([
            'player',
            'position',
            'detailed_position',
            'fielding_percentage',
            'errors',
            'putouts',
            'putouts_per_game',
            'range_factor_per_game',
            'risp_improvement'
        ]).sort("range_factor_per_game",descending=True)

        chk_hitting = chk_df.filter(
            (pl.col('hits') > 0)
        ).select([
            'player',
            'position',
            'detailed_position',
            'batting_avg',
            'at_bats',
            'hits',
            'home_runs',
            'plate_appearances',
            'slugging',
            'obps',
            'HRs_per_game',
            'hit_quality',
            'risp_improvement'
        ]).sort("batting_avg",descending=True)
        chk_pitching = chk_df.filter(
            (pl.col('position') == 'Pitcher')
        ).select([
            'player',
            'position',
            'detailed_position',
            'ERA',
            'walks_hits_per_inning_pitched',
            'appearances',
            'wins',
            'batters_faced_per_appearance',
            'pitches_per_appearance',
            'innings_pitched_per_appearance',
            'strikeout_rate',
            'strikeouts_per_nine',
            'walks_per_nine',
            'home_runs_allowed_per_nine',
            'hits_allowed_per_nine',
            'strikeouts_to_balls_on_base',
            'win_rate',
            'win_chance_improvement',
            'risp_improvement'
        ]).sort("ERA",descending=False)
        if position.lower() == 'infield' or position == 'outfield' or position == 'field' or position == 'fielding':
            return chk_field
        elif position.lower() == 'hitting' or position.lower() == 'batting':
            return chk_hitting
        elif position.lower() == 'pitching' or position.lower() == 'pitcher':
            return chk_pitching
        elif position.lower() == 'all':
            return chk_field, chk_hitting, chk_pitching
                
    def inspect_player(self, name: str) -> None:
        from scouting_report import ScoutReport as scout
        player_object = self.players[self.player_ids[name]]
        temp_stats = player_object.stats.copy()
        temp_stats['Player'] = name
        print(type(self.get_position_df(player_object.simplified_position)))
        player_stats = (self.get_position_df(player_object.simplified_position).columns)
        for col_name in player_stats:
            if col_name not in temp_stats.keys():
                temp_stats[col_name] = 0
        team_scout_df = scout.scout_rep_df().filter(pl.col('Player')==name)
        left_join = pl.DataFrame(temp_stats).join(how='left',other=team_scout_df,on='Player')
        hitting = ['Batting_Topline','Batting_Details','at_bats','batting_avg','slugging','obps','HRs_per_game']
        fielding = ['Defensive_Topline','Defensive_Details','fielding_percentage','range_factor_per_game','putouts_per_game']
        pitching = ['Pitching_Topline','Pitching_Details','ERA','walks_hits_per_inning_pitched','strikeout_rate','win_chance_improvement','win_rate']
        flex_category = []
        match player_object.simplified_position:
            case 'Pitcher':
                flex_category += pitching
            case 'Infield'|'Outfield' | 'Catcher':
                flex_category += fielding + hitting
    
        flex = left_join.select(['Player','detailed_position','Overall']+flex_category)
        transposed = flex.transpose(include_header=True,header_name='Stat',column_names=['Value'])
        return transposed

    def inspect_all(self,print_results=True,print_all=True):
        inspect_array = []
        for player in self.players.values():
            try:
                report = self.inspect_player(player.name)
                if print_results:
                    if print_all:
                        Utils.print_all_rows(report)
                    else:
                        print(report)
                inspect_array.append(report)
            except Exception as e:
                print(f'Error inspecting player {player.name}: {str(e)}')
        return inspect_array
    
    def inspect_keyword(self, keyword: str):
        from scouting_report import ScoutReport as scout
        print(Utils.printout_header(f'Keyword Inspection: {keyword}'))
        scout_players = scout.keyword_search(keyword)
        Utils.print_all(scout_players[0])
        for name in scout_players[1]:
            try:
                Utils.print_all(self.inspect_player(name))
            except Exception as e:
                print(f'Some fucking error or another for {name}: {str(e)}')


class Player:
    def __init__(self,team_object: Team, player_id: str) -> None:
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
        self.extract_stats()
        
    def get_dir(self, builtins: bool = False) -> list:
        result = dir(self)
        if not builtins:
            result[:] = [item for item in result if not item.startswith('__')]
        return result
    
    def ensure_stats(self, debug: bool = False) -> None:
        # makeshift stopgap for when a player doesn't turn up a stat. this is not exhaustive - only for the stats that give me trouble basically.
        stat_options = [
            'appearances', 'assists', 'assists_risp', 'at_bats', 'at_bats_risp', 'caught_double_play', 'caught_double_play_risp', 'caught_stealing', 'caught_stealing_risp', 'doubles', 'doubles_risp',
            'errors', 'errors_risp', 'field_out', 'field_out_risp', 'fielders_choice', 'flyouts', 'flyouts_risp', 'force_outs', 'force_outs_risp', 'grounded_into_double_play',
            'grounded_into_double_play_risp', 'groundout', 'groundout_risp', 'hit_by_pitch', 'hit_by_pitch_risp', 'home_runs', 'home_runs_risp', 'left_on_base',
            'left_on_base_risp', 'lineouts', 'lineouts_risp', 'plate_appearances', 'plate_appearances_risp', 'popouts', 'popouts_risp', 'putouts', 'putouts_risp',
            'reached_on_error', 'reached_on_error_risp', 'runs', 'runs_batted_in', 'runs_batted_in_risp', 'runs_risp', 'sac_flies', 'sac_flies_risp', 'singles',
            'singles_risp', 'stolen_bases', 'stolen_bases_risp', 'struck_out', 'struck_out_risp', 'triples', 'walked', 'walked_risp'
        ]

        for stat in stat_options:
            if stat not in self.stats.keys():
                self.stats[stat] = 0
        if debug:
            print(f'{self.name} stats dict:')
            print(self.stats)

    def extract_stats(self, debug: bool = False) -> dict:
        # simplified positions translate to position-specific KPIs
        # store derived stats in a new file, derived_stats.json
        derived_stats = Utils.access_json('derived_stats.json')

        player_derived_stats = Utils.ensure_nested_dict(derived_stats,self.team.id,self.player_id)# derived_stats[self.team.id][self.player_id]
        
        self.ensure_stats()

        risp_dict = {}
        try:
            for risp_stat, risp_value in self.stats.items():
                if risp_stat[-5:] == '_risp':
                    for std_stat, std_value in self.stats.items():
                        if std_stat == risp_stat[:-5]:
                            risp_dict[std_stat] = {
                                'standard': std_value,
                                'risp':risp_value
                            }
            risp_improvement = 0
            for std_risp_pair in risp_dict.values():
                denominator = len(risp_dict.values())
                if std_risp_pair['standard'] == 0:
                    denominator -= 1
                    continue
                risp_improvement += (std_risp_pair['risp']-std_risp_pair['standard'])/std_risp_pair['standard']
            risp_improvement /= denominator
            self.stats['risp_improvement'] = round(risp_improvement*100,2)
        except Exception as e:
            print('Error getting risp improvement.')
            print(str(e))

        # everyone bats, but apparently pitchers dont get stats
        if self.simplified_position != 'Pitcher':
            batting = {}
            # self.stats['appearances'] = self.team.record['Wins'] + self.team.record['Losses']
            self.stats['appearances'] = self.stats['plate_appearances'] / 3.73

            # 1) total hits
            try:
                hits = (
                    self.stats['singles']
                    + self.stats['doubles']
                    + self.stats['triples']
                    + self.stats['home_runs']
                )
                batting['hits'] = hits
            except Exception:
                batting['hits'] = 0

            # 2) batting average
            try:
                batting['batting_avg'] = hits / self.stats['at_bats']
            except Exception:
                batting['batting_avg'] = 0

            # 3) on-base percentage
            try:
                batting['on_base_percentage'] = (
                    hits
                    + self.stats['walked']
                    + self.stats['hit_by_pitch']
                ) / self.stats['plate_appearances']
            except Exception:
                batting['on_base_percentage'] = 0

            # 4) slugging
            try:
                batting['slugging'] = (
                    self.stats['singles']
                    + 2*self.stats['doubles']
                    + 3*self.stats['triples']
                    + 4*self.stats['home_runs']
                ) / self.stats['at_bats']
            except Exception:
                batting['slugging'] = 0

            # 5) obps
            try:
                batting['obps'] = (
                    batting['on_base_percentage']
                    + batting['slugging']
                )
            except Exception:
                batting['obps'] = 0

            # 6) risp batting avg
            try:
                batting['risp_batting_avg'] = (
                    self.stats['singles_risp']
                    + self.stats['doubles_risp']
                    + self.stats.get('triples_risp', 0)
                    + self.stats['home_runs_risp']
                ) / self.stats['at_bats_risp']
            except Exception:
                batting['risp_batting_avg'] = 0
            # 7) HRs per game
            try:
                batting['HRs_per_game'] = (
                    self.stats['home_runs']/self.stats['appearances']
                )
            except:
                batting['HRs_per_game'] = 0

            # 8) isolated power
            try:
                batting['isolated_power'] = (
                    batting['slugging']
                    - batting['batting_avg']
                )
            except Exception:
                batting['isolated_power'] = 0

            # 9) hit quality
            try:
                batting['hit_quality'] = (
                    self.stats['singles']
                    + 2*self.stats['doubles']
                    + 3*self.stats['triples']
                    + 4*self.stats['home_runs']
                ) / self.stats['hits']
            except Exception:
                batting['hit_quality'] = 0

            player_derived_stats['batting'] = batting
            self.stats.update(batting)

        # infielding
        if self.simplified_position == 'Infield':
            infielding = {}
            try:
                infielding['putouts_per_game'] = self.stats['putouts']/self.stats['appearances']
                infielding['range_factor_per_game'] = (self.stats['putouts'] + self.stats['assists'])/self.stats['appearances']
            except:
                if debug: print('No appearances logged. Mark it zero!')
                infielding['putouts_per_game'] = 0
                infielding['range_factor_per_game'] = 0
            try:
                infielding['fielding_percentage'] = round((self.stats['putouts'] + self.stats['assists'])/(self.stats['putouts'] + self.stats['assists'] + self.stats['errors']),2)
            except Exception as e:
                print(self.name)
                print(e)
                if str(e) == 'division by zero':
                    print(self.stats['putouts'], self.stats['assists'], self.stats['errors'])
                infielding['fielding_percentage'] = 0.0
            try:
                infielding['fielding_percentage_risp'] = (self.stats['assists_risp'] + self.stats['putouts_risp'])/(self.stats['assists_risp'] + self.stats['putouts_risp'] + self.stats['errors_risp'])
                # infielding['fp_risp_improvement'] = infielding['fielding_percentage_risp'] - infielding['fielding_percentage']
            except Exception as e:
                infielding['fielding_percentage_risp'] = 0
                # infielding['fp_risp_improvement'] = 0
            # try:
            #     infielding['risp_diff_percentage'] = infielding['fp_risp_improvement']/infielding['fielding_percentage']
            # except:
            #     infielding['risp_diff_percentage'] = 0

            player_derived_stats['infield'] = infielding
            self.stats.update(infielding)

        if self.simplified_position == 'Outfield':
            outfielding = {}
            try:
                outfielding['putouts_per_game'] = self.stats['putouts']/self.stats['appearances']
                outfielding['range_factor_per_game'] = (self.stats['putouts'] + self.stats['assists'])/self.stats['appearances']
            except:
                if debug: print('No appearances logged. Mark it zero!')
                outfielding['putouts_per_game'] = 0
                outfielding['range_factor_per_game'] = 0
            # try:
            #     outfielding['risp_diff_percentage'] = outfielding['fp_risp_improvement']/outfielding['fielding_percentage']
            # except:
            #     outfielding['risp_diff_percentage'] = 0
            try:
                outfielding['fielding_percentage'] = (self.stats['putouts'] + self.stats['assists'])/(self.stats['putouts'] + self.stats['assists'] + self.stats['errors'])
                outfielding['fielding_percentage_risp'] = (self.stats['assists_risp'] + self.stats['putouts_risp'])/(self.stats['assists_risp'] + self.stats['putouts_risp'] + self.stats['errors_risp'])
                # outfielding['fp_risp_improvement'] = outfielding['fielding_percentage_risp'] - outfielding['fielding_percentage']
            except:
                outfielding['fielding_percentage'] = 0
                outfielding['fielding_percentage_risp'] = 0
                # outfielding['fp_risp_improvement'] = 0

            player_derived_stats['outfield'] = outfielding
            self.stats.update(outfielding)

        if self.simplified_position == 'Catcher':
            catching = {}
            try:
                catching['putouts_per_game'] = self.stats['putouts']/self.stats['appearances']
                catching['range_factor_per_game'] = (self.stats['putouts'] + self.stats['assists'])/self.stats['appearances']
            except:
                if debug: print('No appearances logged. Mark it zero!')
                catching['putouts_per_game'] = 0
                catching['range_factor_per_game'] = 0
            # try:
            #     catching['risp_diff_percentage'] = catching['fp_risp_improvement']/catching['fielding_percentage']
            # except:
            #     catching['risp_diff_percentage'] = 0
            try:
                catching['fielding_percentage'] = (self.stats['putouts'] + self.stats['assists'])/(self.stats['putouts'] + self.stats['assists'] + self.stats['errors'])
                catching['fielding_percentage_risp'] = (self.stats['assists_risp'] + self.stats['putouts_risp'])/(self.stats['assists_risp'] + self.stats['putouts_risp'] + self.stats['errors_risp'])
                # catching['fp_risp_improvement'] = catching['fielding_percentage_risp'] - catching['fielding_percentage']
            except:
                catching['fielding_percentage'] = 0
                catching['fielding_percentage_risp'] = 0
                # catching['fp_risp_improvement'] = 0

            player_derived_stats['outfield'] = catching
            self.stats.update(catching)
        
        if self.simplified_position == 'Pitcher':
            pitching = {}

            outs = self.stats.get('outs', 0)
            appearances = self.stats.get('appearances', 0)
            batters_faced = self.stats.get('batters_faced', 0)
            pitches_thrown = self.stats.get('pitches_thrown', 0)
            wins = self.stats.get('saves', 0) if self.position == 'CL' else self.stats.get('wins',0)
            earned_runs = self.stats.get('earned_runs', 0)
            walks = self.stats.get('walks', 0)
            hits_allowed = self.stats.get('hits_allowed', 0)
            home_runs_allowed = self.stats.get('home_runs_allowed', 0)
            strikeouts = self.stats.get('strikeouts', 0)

            pitching['innings_pitched'] = outs / 3

            try:
                if appearances > 0:
                    pitching['batters_faced_per_appearance'] = batters_faced / appearances
                    pitching['pitches_per_appearance'] = pitches_thrown / appearances
                    pitching['innings_pitched_per_appearance'] = pitching['innings_pitched'] / appearances
                    pitching['win_rate'] = wins / appearances
                else:
                    pitching['batters_faced_per_appearance'] = 0
                    pitching['pitches_per_appearance'] = 0
                    pitching['innings_pitched_per_appearance'] = 0
                    pitching['win_rate'] = 0

                ippa = pitching['innings_pitched_per_appearance']
                if ippa > 0:
                    pitching['batters_faced_per_inning'] = pitching['batters_faced_per_appearance'] / ippa
                else:
                    pitching['batters_faced_per_inning'] = 0

                pitching['strikeout_rate'] = strikeouts / batters_faced if batters_faced else 0
                pitching['ERA'] = (earned_runs * 9) / pitching['innings_pitched'] if pitching['innings_pitched'] else 0
                pitching['walks_hits_per_inning_pitched'] = (
                    (walks + hits_allowed) / pitching['innings_pitched']
                    if pitching['innings_pitched'] else 0
                )

                pitching['strikeouts_per_nine'] = (strikeouts * 9) / pitching['innings_pitched'] if pitching['innings_pitched'] else 0
                pitching['walks_per_nine'] = (walks * 9) / pitching['innings_pitched'] if pitching['innings_pitched'] else 0
                pitching['home_runs_allowed_per_nine'] = (home_runs_allowed * 9) / pitching['innings_pitched'] if pitching['innings_pitched'] else 0
                pitching['hits_allowed_per_nine'] = (hits_allowed * 9) / pitching['innings_pitched'] if pitching['innings_pitched'] else 0

                pitching['strikeouts_to_balls_on_base'] = strikeouts / walks if walks else 0
                
                team_wins = self.team.record.get('Wins', 0)
                team_losses = self.team.record.get('Losses', 0)
                team_total = team_wins + team_losses
                team_win_rate = (team_wins / team_total) if team_total else 0
                pitching['win_chance_improvement'] = (
                    ((pitching['win_rate'] / self.team.win_rate) - 1)*100
                    if team_win_rate else 0
                )

            except Exception as e:
                # if debug, show the error
                print("Pitcher stats error:", e)
                # ensure all keys exist, defaulting to zero
                for key in [
                    'batters_faced_per_appearance','pitches_per_appearance',
                    'innings_pitched_per_appearance','win_rate','innings_pitched',
                    'batters_faced_per_inning','strikeout_rate','ERA',
                    'walks_hits_per_inning_pitched','strikeouts_per_nine',
                    'walks_per_nine','home_runs_allowed_per_nine',
                    'hits_allowed_per_nine','strikeouts_to_balls_on_base',
                    'win_chance_improvement'
                ]:
                    pitching.setdefault(key, 0)

            player_derived_stats['pitcher'] = pitching
            self.stats.update(pitching)

        for key, value in self.stats.items():
            self.stats[key] = round(value, 4)
        Utils.write_json('derived_stats.json', derived_stats)

if __name__ == '__main__':
    beetles = Team(lady_beetles)
    #print(beetles.team_data)
