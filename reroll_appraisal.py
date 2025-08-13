import requests
from utils import Utils

class Player:
    def __init__(self,name,stats = {},position = '', team_id = '680e477a7d5b06095ef46ad1'):
        self.name = name
        self.team_id = team_id
        self.categories = {}
        self.stats = stats
        self.position = position
        value_dicts = list(Utils.access_json('player_attributes.json').values()) # list of player attrs and attr cats
        for val_dict in value_dicts: # loop through value dicts and set up self.cats as one of each cat and component attr
            for category, inner_dict in val_dict.items():
                if not isinstance(inner_dict, dict):
                    continue
                if category not in self.categories:
                    self.categories[category] = set()
                self.categories[category].update(inner_dict.keys())
        print(self.categories)
    
    def retrieve_cached_attrs(self):
        try:
            player_id = self.get_player(self.name, debug=False)
        except:
            print('Error finding player id.')
            return
        player_attrs = {}
        team_attrs = Utils.access_json('attributes_db.json')[self.team_id]
        for ind, player in enumerate(team_attrs):
            if list(player.keys())[0] == player_id:
                player_attrs = team_attrs[ind][player_id]
                self.stats = player_attrs[self.position]
                print('Found player stats in db.')
                return player_attrs
        print(f'Could not find stats.')
        return

    def collect_attrs(self):
        print(f'Collecting attributes for {self.name}...')

        # Prompt user to choose a position (category)
        for cat_name in self.categories:
            choice = input(f"Use category '{cat_name}'? (y/n): \n").strip().lower()
            if choice == 'y':
                self.position = cat_name
                break

        # If no category selected
        if not self.position:
            print("No valid category selected. Please restart and choose a category.")
            return

        # Collect attribute values for the selected category
        for attr in sorted(self.categories[self.position]):
            while True:
                val = input(f"Enter a number for '{attr}' (stars): \n").strip()
                try:
                    self.stats[attr] = float(val)
                    print(self.stats)
                    break
                except ValueError:
                    print(f"Invalid input. Please enter a numeric value for '{attr}'.")
    
    def get_coefficients(self):
        match self.position:
            case "Pitching":
                print('pitching')
                significant_whip_coefs = {
                    "stat": "WHIP",
                    "const": 2.175,
                    "Accuracy": -0.0206,
                    "Control": -0.0534,
                    "Persuasion": -0.0318,
                    "Presence": -0.0205,
                    "Rotation": -0.0219,
                    "Stuff": -0.0381,
                    "Velocity": -0.0497
                }
                significant_era_coefs = {
                    "stat": "ERA",
                    "const": 8.6221,
                    #"Accuracy": 0.0704,
                    "Control": -0.1962,
                    "Defiance": -0.0120,
                    "Persuasion": -0.1544,
                    "Presence": -0.1499,
                    "Rotation": -0.2213,
                    "Stamina": -0.1380,
                    "Stuff": -0.2486,
                    "Velocity": -0.219
                }
                return [significant_whip_coefs, significant_era_coefs]
            case "Batting"|"Hitting":
                print('hitting')
                significant_obps_coefs = {
                    "stat": "OBPS",
                    "const": 0.5610,
                    "Aiming": 0.0161,
                    "Contact": 0.0148,
                    #"Cunning": 0.0057,
                    #"Determination": 0.0029,
                    "Discipline": 0.0077,
                    #"Insight": 0.0048,
                    #"Intimidation": 0.0063,
                    "Lift": 0.0107,
                    "Muscle": 0.0213,
                    #"Selflessness": -3.439e-05,
                    #"Vision": -0.0018,
                    #"Wisdom": 0.0060,
                }
                significant_obp_coefs = {
                    "stat": "OBP",
                    "const": 0.2935,
                    "Aiming": 0.0065,
                    #"Contact": 0.0003,
                    #"Cunning": 0.0024,
                    "Determination": 0.0031,
                    "Discipline": 0.0080,
                    #"Insight": 0.0021,
                    "Intimidation": 0.0032,
                    #"Lift": 0.0002,
                    "Muscle": 0.0035,
                    #"Selflessness": -0.0002,
                    #"Vision": -0.0015,
                    #"Wisdom": 0.0008,
                }
                significant_home_runs_coefs = {
                    "stat": "HRs_per_AB",
                    "const": 0.0150,
                    #"Aiming": 0.1234,
                    "Contact": 0.002,
                    #"Cunning": 0.1178,
                    #"Determination": -0.0556,
                    #"Discipline": -0.1257,
                    #"Insight": 0.1110,
                    #"Intimidation": 0.0606,
                    "Lift": 0.0024,
                    "Muscle": 0.0035,
                    #"Selflessness": 0.0813,
                    #"Vision": 0.1549,
                    #"Wisdom": 0.1167,
                }
                result = [significant_obps_coefs, significant_obp_coefs, significant_home_runs_coefs]
                print(result)
                return result
            case _:
                "Not sure what you need me to do boss. The position didnt match the appraisal stuff"
                return
    
    def generate_appraisal(self):
        if not self.stats:
            self.collect_attrs()
            print(self.stats)
        # coefs = self.get_coefficients()
        # print(self.get_coefficients())
        results_dict = {}
        for coef_dict in self.get_coefficients():
            total = 0
            for attr, value in self.stats.items():
                total += coef_dict.get(attr,0)*value
            results_dict[f'Estimated {coef_dict['stat']} bonus'] = round(total,3)
        return results_dict
    
    def get_player(self, name, printout:bool = False, just_id:bool = True, debug: bool = False) -> dict:
        base_url = 'https://mmolb.com/api/'
        r = requests.get(f'{base_url}/team/{self.team_id}')
        if debug:
            print(r.json())
        for player in r.json()['Players']:
            if f'{player['FirstName']} {player['LastName']}' == name:
                player_id = player['PlayerID']
                player_data = requests.get(f'{base_url}/player/{player_id}').json()
                if printout:
                    print(player_data)
                    return(player_data)
                if just_id:
                    return player_id
                return player_data
        print('Name not found. Does the player exist yet? Did you use the full name?')


def run_the_thing(player_obj):
    player_obj.retrieve_cached_attrs()
    print(player_obj.generate_appraisal())

if __name__ == "__main__": 
    changming = Player('Changming Mercedes',position = 'Batting', team_id = '688847f85cb20f9e396ef60b')
    milani = Player('Milani Kumar',position = 'Batting', team_id = '688847f85cb20f9e396ef60b')
    stacey = Player('Stacey Morita',position = 'Batting', team_id = '688847f85cb20f9e396ef60b')
    for player in [changming, stacey,milani]:
        print(player.name)
        run_the_thing(player)