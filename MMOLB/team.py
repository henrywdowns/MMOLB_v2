import pprint
from .stat_calcs import MMOLBStats

class _TeamCommon:
    def __init__(self, team_data, api_handler):
        self._data = team_data
        self.api_handler = api_handler
        self.attributes = None
    # shared helpers only (no behavior changes)
    def help(self, attrs: bool = False, methods: bool = False, printout=True):
        if printout: print(f'======== {self.__class__.__name__} Class Help ========')
        _attrs = [k for k in self.__dict__.keys()]
        _methods = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
        attrs_methods = [_attrs, _methods]
        if attrs: attrs_methods = _attrs
        elif methods: attrs_methods = _methods
        if printout: print(attrs_methods)
        return attrs_methods

    def get_player(self, key: str):
        import re
        if re.search(r"\d", key):
            _players_by_id = {ply.id: ply for ply in self.players}
            return _players_by_id[key]
        else:
            _players_by_name = {ply.full_name: ply for ply in self.players}
            return _players_by_name[key]
        
    def run_stats(self,truncate=True):
        team_stats = MMOLBStats(self._data, api_handler=self.api_handler, _class_type = self.__class__.__name__)
        df_dict = team_stats.master_summary()
        for k, df in df_dict.items():
            if k in ['hitting', 'pitching'] and truncate:
                df_dict[k] = df[df['team_id'] == self._id]
                if k == 'hitting':
                    df_dict[k] = df[df['positiontype'] == 'Batter'] 
                else:
                    df_dict[k] = df[df['positiontype'] == 'Pitcher']
        return df_dict
    
    def _get_attributes(self) -> dict:
        player_attrs = {} # key = player full name, value = stats
        if self.__class__.__name__ == 'LightTeam': # this works much more smoothly for LightTeam since it's all immediately available
            for player in self.players:
                attrs = player['Talk']
                attrs_dict = {
                    'total_attr_dict': {k.capitalize(): {} for k in attrs.keys()}, # total attributes
                    'base_attr_dict': {k.capitalize(): {} for k in attrs.keys()}, # base attributes
                    'equip_attr_dict': {k.capitalize(): {} for k in attrs.keys()} # total minus base attributes
                }

                for cat in attrs.keys():
                    stars = attrs[cat]['stars'] # it's called stars, but we now have fine-grain numbers. bye stars! 
                    attrs_dict['total_attr_dict'][cat] = {k: v['total'] for k, v in stars.items()}
                    attrs_dict['base_attr_dict'][cat] = {k: v['base_total'] for k, v in stars.items()}
                    attrs_dict['equip_attr_dict'][cat] = {k:round(v['total']-v['base_total'],2) for k, v in stars.items()}

                full_name = f'{player['FirstName']} {player['LastName']}'
                player_attrs[full_name] = attrs_dict
            return player_attrs
        elif self.__class__.__name__ == 'Team': # might as well build it into Team. just iterate through players and access the right attributes.
            for player in self.players:
                player_attrs[player.full_name] = player.attributes
            return player_attrs

class Team(_TeamCommon): # really a vehicle for looking for extremely team-specific stats. LightTeam is better for anything player-focused.
    def __init__(self, team_data: dict, api_handler) -> None:
        super().__init__(team_data, api_handler)
        for k, v in self._data.items():
            setattr(self, k.lower(), v)
        self.player_data = self.players  # original player data from the json response.
        # use self.players for Player objects. the APIHandler overwrites self.players with Player objects after initialization.

    def get_roster(self, roster_type: str = None) -> dict:
        t = self._data
        roster = {
            "Players": t.get("Players"),
            "Bench": t.get("Bench")
        }
        if roster_type:
            roster_type = roster_type.capitalize()
            roster = {roster_type: roster.get(roster_type)}
        return roster

class LightTeam(_TeamCommon):  # lighter weight class for batch requests. delivers far more player information far faster, but has less team data.
    def __init__(self, team_data: dict, api_handler) -> None:
        super().__init__(team_data, api_handler)
        self._data = team_data
        for k, v in self._data.items():
            setattr(self, k.lower(), v)
        self.player_ids = self.players
        self.players = [] # objects. created after instantiation in APIHandler