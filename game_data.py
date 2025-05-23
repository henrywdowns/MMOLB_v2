import requests
import json

class GameLog:
    def __init__(self,team_object: object) -> None:
        self.team = team_object
        self.team_id = team_object.id
        self.player_ids = [player for player in self.team.player_ids.values()]
        self.appearances = {}
        with open('games.json','r') as f:
            file = json.load(f)
            self.game_ids = file.get(self.team_id)
            if self.game_ids is None:
                print('WARNING: ID not found. self.game_ids is NoneType.')
    
    def get_appearances(self) -> dict:
        # Load existing file or create fresh structure
        try:
            with open('games.json', 'r') as f:
                file = json.load(f)
        except FileNotFoundError:
            file = {}

        if 'appearances' not in file:
            file['appearances'] = {}

        appearances = file['appearances']

        # Build reverse index of games already logged
        existing_game_ids = set()
        for games in appearances.values():
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

        return appearances
    

if __name__ == '__main__':
    pass