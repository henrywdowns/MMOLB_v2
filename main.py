import spicy_chicken_stats as scs
from utils import Utils
import requests

chicken_id = '680e477a7d5b06095ef46ad1'
lady_beetles = '6805db0cac48194de3cd407c'
seers = '6805db0cac48194de3cd40b5'

beetles = scs.Team(lady_beetles)
seers = scs.Team(seers)


def new_team(team_id):
    new_team = scs.Team(team_id)
    new_team.get_game_history()
    for player in new_team.players.values():
        player.extract_stats()
    if new_team in Utils.access_json('games.json').values():
        print('Team loaded up and derived stats saved!')
    else:
        print('Something is wrong and I\'m too lazy to tell you exactly what.')
teams = [beetles,seers]

# print(beetles.players['6805db0cac48194de3cd407d'].simplified_position)
# for player in beetles.players.values():
#     print(f'{player.name}: {player.position}')
# for line in beetles.team_df.items():
#     print(line)

sample_players = {
    'kibbles_swift':seers.players[seers.player_ids['Kibbles Swift']],
    'taylor_mogensen':seers.players[seers.player_ids['Taylor Mogensen']],
    'fizz_kaneko':seers.players[seers.player_ids['Fizz Kaneko']],
    'null_baba':seers.players[seers.player_ids['Null Baba']]
    }

# for player in sample_players.values():
#     print(f'{player.name} -- {player.simplified_position}\n{player.stats.keys()}')

# beetles.get_game_history()

# for player in beetles.players.values():
#     player.extract_stats()

# games = Utils.access_json('games.json')
# print(games['last_update'])

# print(beetles.players['6805db0cac48194de3cd407d'].name)
# print(beetles.players['6805db0cac48194de3cd407d'].position)
# print(beetles.players['6805db0cac48194de3cd407d'].stats)

nicole = requests.get('https://mmolb.com/player/6805db0cac48194de3cd407d').json
print(nicole)

# for playername, id in seers.player_ids.items():
#     print(f'{playername} -- {seers.players[id].simplified_position}')

#TODO: figure out why some players are loading in stats as {} (ie nicole humphrey 6805db0cac48194de3cd407d)