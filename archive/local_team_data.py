import json

class TeamStorage:
    def __init__(self):
        self.file = self.get_file()

    def get_file(self,filename='teams.json'):
        try:
            with open('teams.json','r') as f:
                file = json.load(f)
        except Exception as e:
            print(f'Retrieval failed. Error: \n{str(e)}')
            return None
        return file
    
    def options(self):
        file = list(self.file.items())[0][1].keys()
        print(file)

    def summarize_local_data(self,players=False,team=None):
        file = dict(self.file)
        for item in file.values():
            players = [f'{player['FirstName']} {player['LastName']} -- {player['Position']}' for player in item['Players']]
            if not team:
                print(f'{item['Abbreviation']} {item['Name']} {item['Emoji']} -- {item['Record']}')
                if players:
                    print('\nPlayers:\n')
                    for player in players:
                        print(player)
            elif item['Name'] == team or item['_id'] == team:
                print(f'{item['Emoji']}  {item['Abbreviation']} {item['Name']} -- W: {item['Record']['Regular Season']['Wins']} | L: {item['Record']['Regular Season']['Losses']} | Run Diff: {item['Record']['Regular Season']['RunDifferential']}')
                if players:
                    print('\nPlayers:\n')
                    for player in players:
                        print(player)
                return
        print(f"Team {team} not found in data.")
        return
    
    def get_team_data(self,team_id=None):
        if team_id:
            try:
                json_dict = self.get_file()
                team_data = json_dict[team_id]
                return team_data
            except Exception as e:
                print(f'Error! Did you use the team\'s ID? {str(e)}')

if __name__ == '__main__':
    teams_json = TeamStorage()
    teams_json.summarize_local_data(team='Seers')