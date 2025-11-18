from tqdm import tqdm
import pandas as pd

# TODO: sort out league population. right now returning NA for team_name all the way down, seemingly.

class League:
    def __init__(self, league_data: dict) -> None:
        self._data = league_data
        self.teams = None # API class will populate this in get_league()
        for k, v in self._data.items(): # unpack self._data json response and assign as attributes
            setattr(self, k.lower(), v)
        self.size = len(self.teams)
        
    def help(self,attrs: bool = False,methods: bool = False, printout = True):
        if printout: print('======== League Class Help ========')
        _attrs = [k for k in self.__dict__.keys()]
        _methods = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
        attrs_methods = [_attrs,_methods]
        if attrs: attrs_methods = _attrs
        elif methods: attrs_methods = _methods
        if printout: print(attrs_methods)
        return attrs_methods
    
    def get_team(self, key: str):
        import re
        try:
            if re.search(r"\d", key):
                _teams_by_id = {tm._id: tm for tm in self.teams}
                return _teams_by_id[key]
            else:
                _teams_by_name = {tm.name: tm for tm in self.teams}
                return _teams_by_name[key]
        except Exception as e:
            print(e)
            print(key)
        
    def league_statistics(self):
        # hacky method that passes a component team into MMOLBStats and returns just the league stuff since freecashe.ws passes both JSONs on the team endpoint
        from MMOLB import MMOLBStats
        import numpy as np
        component_team = self.teams[0]
        stats_obj = MMOLBStats(component_team,component_team.api_handler,self.__class__.__name__)
        league_stats = {
            'batting': stats_obj.basic_hitting('league'),
            'pitching': stats_obj.basic_pitching('league')
        }

        for df in league_stats.values():
            df['league_name'] = self.name
            df['league_id'] = self._id
            df.dropna(subset=['team_id'], inplace=True)
            # tm_ids_names = {tm._id: tm.name for tm in self.teams}
            df.insert(loc=3, column='team_name', value=df['team_id'].map(self.names_by_id))
            try:
                win_diff_by_id = {
                    tm._id: (tm.record['Regular Season']['Wins'] - tm.record['Regular Season']['Losses'])
                    for tm in self.teams
                }

                df.insert(loc=3, column='team_name', value=df['team_id'].map(self.names_by_id))
                df['team_win_diff'] = df['team_id'].map(win_diff_by_id).astype('float64')
            except Exception:
                df['team_win_diff'] = np.nan
        return league_stats
    
    def league_attributes(self):
        # NOTE: use index=False when making this a csv or it will save the index as a new col.
        if getattr(self,'_populate_status').lower() == 'all':
            league_attrs = pd.concat(
                [team.get_attributes(flat=True) for team in self.teams],
                ignore_index=True
            )
            league_attrs = league_attrs[league_attrs['team'].notna()]
            league_attrs['team_win_diff'] = league_attrs['team'].apply(
                lambda x: self.get_team(x).record['Regular Season']['Wins'] - self.get_team(x).record['Regular Season']['Losses']
            )
            league_attrs['position_type'] = [
                self.get_team(t).get_player(p)['PositionType']
                for t, p in zip(league_attrs['team'], league_attrs['player'])
            ]
            return league_attrs
        else:
            raise RuntimeError('You must populate League object with all (populate=\'all\') to check league attributes. Access Team or LightTeam attributes instead if only looking at one team.')