import pprint
from .stat_calcs import MMOLBStats
import pandas as pd

class _TeamCommon:
    def __init__(self, team_data, api_handler):
        self._data = team_data
        self.api_handler = api_handler
        self.attributes = None

    # shared attrs + funcs only (nothing specific)
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
            if self.__class__.__name__ == 'Team':
                _players_by_name = {ply.full_name: ply for ply in self.players}
            elif self.__class__.__name__ == 'LightTeam':
                _players_by_name = {f'{ply['FirstName']} {ply['LastName']}': ply for ply in self.players}
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
    
    import pandas as pd

    def get_attributes(self, flat=False, debug=False):
        # flat returns an analytics-ready df
        player_attrs = {}

        if self.__class__.__name__ == 'LightTeam':
            for player in self.players:
                try:
                    attrs = player['Talk']
                    attrs_dict = {
                        kind: {k.capitalize(): {} for k in attrs.keys()}
                        for kind in ('total_attr_dict', 'base_attr_dict', 'equip_attr_dict')
                    }

                    for cat, stars in attrs.items():
                        attrs_dict['total_attr_dict'][cat] = {k: v['total'] for k, v in stars['stars'].items()}
                        attrs_dict['base_attr_dict'][cat] = {k: v['base_total'] for k, v in stars['stars'].items()}
                        attrs_dict['equip_attr_dict'][cat] = {k: round(v['total']-v['base_total'],2) for k, v in stars['stars'].items()}

                    full_name = f"{player['FirstName']} {player['LastName']}"
                    player_attrs[full_name] = attrs_dict
                except Exception as e:
                    if debug:
                        print(e)
                    else:
                        pass
                        

        elif self.__class__.__name__ == 'Team':
            for player in self.players:
                player_attrs[player.full_name] = player.attributes

        if not flat:
            return player_attrs

        # flatten for analytics
        rows = []
        for player_name, attr_groups in player_attrs.items():
            for group_name, categories in attr_groups.items():
                for category_name, stats in categories.items():
                    for stat_name, value in stats.items():
                        rows.append({
                            "team": self.name,
                            "player": player_name,
                            "group": group_name.replace('_attr_dict',''),
                            "category": category_name,
                            "stat": stat_name,
                            "value": value
                        })

        return pd.DataFrame(rows)


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
        self.players = [] # big dict of players. created after instantiation in APIHandler