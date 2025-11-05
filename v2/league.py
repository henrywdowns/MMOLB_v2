class League:
    def __init__(self, league_data: dict) -> None:
        self._data = league_data
        print(self._data)
        self.teams = None # API class will populate this in get_league()
        for k, v in self._data.items(): # unpack self._data json response and assign as attributes
            setattr(self, k.lower(), v) # 
        