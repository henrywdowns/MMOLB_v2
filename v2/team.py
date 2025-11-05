from player import Player
from stat_calcs import MMOLBStats

class Team:
    def __init__(self,team_data: dict,api_handler) -> None:
        self._team_data = team_data
        self.api_handler = api_handler
        for k, v in self._team_data.items(): # unpack self._team_data json response and assign as attributes
            setattr(self, k.lower(), v)
        self.player_data = self.players # API class populates this in its get_team() method. this is also doable via setattr() but then i'd forget this exists :)

    def help(self,attrs: bool = False,methods: bool = False, printout = True):
        if printout: print('======== Team Class Help ========')
        _attrs = [k for k in self.__dict__.keys()]
        _methods = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
        attrs_methods = [_attrs,_methods]
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
    
    def run_stats(self):
        team_stats = MMOLBStats(self._team_data, api_handler = self.api_handler)
        return team_stats.master_summary()
    
class LightTeam: # lighter weight class for batch requests
    def __init__(self, team_data: dict) -> None:
        self._data = team_data
        for k, v in self._data.items(): # unpack self._team_data json response and assign as attributes
            setattr(self, k.lower(), v)
        self.players = []

    def get_player(self, key: str):
        import re
        if re.search(r"\d", key):
            _players_by_id = {ply.id: ply for ply in self.players}
            return _players_by_id[key]
        else:
            _players_by_name = {ply.full_name: ply for ply in self.players}
            return _players_by_name[key]