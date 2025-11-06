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
        import pandas as pd
        