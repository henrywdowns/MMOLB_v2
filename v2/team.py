from player import Player
from stat_calcs import MMOLBStats

class _TeamCommon:
    def __init__(self, team_data, api_handler):
        self._data = team_data
        self.api_handler = api_handler
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

class Team(_TeamCommon):
    def __init__(self, team_data: dict, api_handler) -> None:
        super().__init__(team_data, api_handler)
        for k, v in self._data.items():
            setattr(self, k.lower(), v)
        self.player_data = self.players  # unchanged, gets changed in APIHandler

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

class LightTeam(_TeamCommon):  # lighter weight class for batch requests
    def __init__(self, team_data: dict, api_handler) -> None:
        super().__init__(team_data, api_handler)
        self._data = team_data
        for k, v in self._data.items():
            setattr(self, k.lower(), v)
        self.player_ids = self.players
        self.players = []