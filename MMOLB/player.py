class Player:
    def __init__(self, player_data: dict) -> None:
        self._data = player_data
        for k, v in self._data.items(): # unpack self._data json response and assign as attributes
            setattr(self, k.lower(), v)
        self.full_name = f'{self._data['FirstName']} {self._data['LastName']}'
        self.attributes = self._get_attributes()
    
    def help(self,attrs: bool = False,methods: bool = False, printout = True):
        if printout: print('======== Player Class Help ========')
        _attrs = [k for k in self.__dict__.keys()]
        _methods = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
        attrs_methods = [_attrs,_methods]
        if attrs: attrs_methods = _attrs
        elif methods: attrs_methods = _methods
        if printout: print(attrs_methods)
        return attrs_methods
    
    def _get_attributes(self):
        attrs = self._data['Talk']
        attrs_dict = {
            'total_attr_dict': {k.capitalize(): {} for k in attrs.keys()},
            'base_attr_dict': {k.capitalize(): {} for k in attrs.keys()},
            'equip_attr_dict': {k.capitalize(): {} for k in attrs.keys()}
        }

        for cat in attrs.keys():
            stars = attrs[cat]['stars']
            attrs_dict['total_attr_dict'][cat] = {k: v['total']*100 for k, v in stars.items()}
            attrs_dict['base_attr_dict'][cat] = {k: v['base_total']*100 for k, v in stars.items()}
            attrs_dict['equip_attr_dict'][cat] = {k:round(v['total']-v['base_total'],2)*100 for k, v in stars.items()}

        return attrs_dict