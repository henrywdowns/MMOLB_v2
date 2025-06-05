import spicy_chicken_stats as scs
from utils import Utils

chicken_id = '680e477a7d5b06095ef46ad1'
lady_beetles = '6805db0cac48194de3cd407c'
seers = '6805db0cac48194de3cd40b5'

beetles = scs.Team(lady_beetles)
seers = scs.Team(seers)


sample_players = {
    'kibbles_swift':seers.players[seers.player_ids['Kibbles Swift']],
    'taylor_mogensen':seers.players[seers.player_ids['Taylor Mogensen']],
    'fizz_kaneko':seers.players[seers.player_ids['Fizz Kaneko']],
    'null_baba':seers.players[seers.player_ids['Null Baba']]
    }
wildcard_team = beetles
wildcard_sample = wildcard_team.players[wildcard_team.player_ids['Nicole Humphrey']]

print(Utils.printout_header(wildcard_sample.name,'<>'))
print(f'{wildcard_sample.stats}')

# print(seers.players['6807f4114251378d1ace1328'].name)
# print(seers.players['6807f4114251378d1ace1328'].position)

# for playername, id in seers.player_ids.items():
#     print(f'{playername} -- {seers.players[id].simplified_position}')


# TODO: stat lists for simplified_positions, implementing calculations, appending to player data