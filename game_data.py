import requests
import json

class GameLog:
    def __init__(self,team_object: object) -> None:
        self.team = team_object
        self.team_id = team_object.id
        self.player_ids = [player for player in self.team.player_ids.values()]
        try:
            with open('games.json','r') as f:
                file = json.load(f)
                self.game_ids = file.get(self.team_id)
                if self.game_ids is None:
                    print('WARNING: ID not found. self.game_ids is NoneType.')
        except Exception as e:
            print(f'WARNING: file not found - initializing empty game IDs. \n{str(e)}')
        self.appearances = {}
        self.get_appearances()
    
    def get_appearances(self) -> dict:
        # Load existing file or create fresh structure
        try:
            with open('games.json', 'r') as f:
                file = json.load(f)
        except FileNotFoundError:
            file = {}

        # set up 'appearances' key at root of json
        if 'appearances' not in file.keys():
            file['appearances'] = {}
    
        # declare appearances for straightforward access
        if self.team_id not in file['appearances']:
            file['appearances'][self.team_id] = {}
        appearances = file['appearances'][self.team_id]

        # Build reverse index of games already logged
        existing_game_ids = set() # no duplicate game ids
        for games in appearances.values(): # sift through existing data (if any) and add to the set
            existing_game_ids.update(games)

        for game_id in self.game_ids:
            game_id_str = str(game_id)
            if game_id_str in existing_game_ids:
                continue  # Already logged somewhere

            # Fetch and parse live game data
            try:
                print(f'Fetching appearances for game {game_id}...')
                game_data = requests.get(f'https://mmolb.com/api/game/{game_id}').json()
                stats = game_data['Stats'][str(self.team_id)]
                for player_id in stats.keys():
                    if player_id not in appearances:
                        appearances[player_id] = []
                    appearances[player_id].append(game_id_str)
                print(f'Successfully got game {game_id} appearances.')
            except Exception as e:
                print(f"Error fetching or processing game {game_id}: {e}")

        # Save updated data
        with open('games.json', 'w') as f:
            json.dump(file, f, indent=2)
        
        self.appearances = appearances
        return appearances
    

if __name__ == '__main__':
    pass