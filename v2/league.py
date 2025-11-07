from tqdm import tqdm

class League:
    def __init__(self, league_data: dict) -> None:
        self._data = league_data
        self.teams = None # API class will populate this in get_league()
        for k, v in self._data.items(): # unpack self._data json response and assign as attributes
            setattr(self, k.lower(), v) # 
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
        if re.search(r"\d", key):
            _teams_by_id = {tm._id: tm for tm in self.teams}
            return _teams_by_id[key]
        else:
            _teams_by_name = {tm.name: tm for tm in self.teams}
            return _teams_by_name[key]
        
    def league_statistics(self):
        # hacky method that passes a component team into MMOLBStats and returns just the league stuff
        from stat_calcs import MMOLBStats
        component_team = self.teams[0]
        stats_obj = MMOLBStats(component_team,component_team.api_handler,self.__class__.__name__)
        league_stats = {
            'hitting': stats_obj.basic_hitting('league'),
            'pitching': stats_obj.basic_pitching('league')
        }
        for df in league_stats.values():
            df['league_name'] = self.name
            df['league_id'] = self._id
            tm_ids_names = {tm._id: tm.name for tm in self.teams}
            df.insert(loc=3, column='team_name', value=df['team_id'].map(tm_ids_names))
        return league_stats


    # this might be unnecessary if i can just tap the freecashews api for the whole league  
    # def league_statistics(self):
    #     import pandas as pd
    #     combined = {
    #         "hitting": [],
    #         "pitching": [],
    #         "team_plus_minus": [],
    #         "league_means": [],   # may just take 1 row, but no harm in concatenating
    #     }
    #     for t in tqdm(self.teams,desc=f'Pulling performance for {t}'):
    #         team_stats_dict = t.run_stats()
    #         for k, v in team_stats_dict:
    #             combined[k].append(v)

    #     for key in combined:
    #         combined[key] = pd.concat(combined[key], ignore_index=True)

    #     return combined