import requests, pprint

class APIHandler:
    def __init__(self,team_id: str ='680e477a7d5b06095ef46ad1') -> None:
        self.base_url = r'https://mmolb.com/api/'
        self.cashews = r'https://freecashe.ws/'
        self.team = r'team'
        self.teams = r'teams'
        self.player = r'player'
        self.team_id = team_id

    def get_team(self) -> dict:
        r = requests.get(f'{self.base_url+self.team}/{self.team_id}')
        return r.json()

    def get_roster(self,roster_type: str = None) -> dict:
        t = self.get_team()
        roster = {
            "Players": t.get("Players"),
            "Bench": t.get("Bench")
        }
        if roster_type:
            roster_type = roster_type.capitalize()
            roster = {roster_type: roster.get(roster_type)}
        return roster
    
    def full_roster(self) -> list: # this needs a closer look...
        r = self.get_roster()
        full_roster = []
        full_roster.append(r['Players'])
        full_roster.append(r['Bench'])
        return full_roster

class Player:
    def __init__(self, player_id: str) -> None:
        self.id = player_id
        self.base_url = r'https://mmolb.com/api/player'
        self.data = self.get_player_data()
        self.full_name = f'{self.data['FirstName']} {self.data['LastName']}'
        self.augments = self.data['Augments']
        self.bats = self.data['Bats']
        self.durability = self.data['Durability']
        self.equipment = self.data['Equipment']
        self.greaterboon = self.data['GreaterBoon']
        self.lesserboon = self.data['LesserBoon']
        self.modifications = self.data['Modifications']
        self.position = self.data['Position']
        self.position_type = self.data['PositionType']
        self.stats = self.data['Stats']
        self.attributes 
    
    def get_player_data(self):
        r = requests.get(f'{self.base_url}/{self.id}')
        pprint.pprint(r.json())
    
    def get_attributes(self):
        attrs_dict = {
            'total_attr_dict': {
                'batting':{},
                'pitching':{},
                'defense':{},
                'baserunning': {}
            },
            'base_attr_dict': {
                'batting':{},
                'pitching':{},
                'defense':{},
                'baserunning': {}
            }
        }
        attrs = self.data['Talk']
        for attr_type in ['total_attr_dict','base_attr_dict']:
            for category,values in attrs.items():
                if attr_type == 'total_attr_dict':
                    # dict -> 'total_attr_dict' -> batting -> ['stars'] -> iterate thru attrs -> bases_total or total depending
                    attrs_dict[attr_type][category]



    

if __name__ == '__main__':
    chk = APIHandler()
    jesse = Player('6841bd7008b7fc5e21e8b02a')