import spicy_chicken_stats as scs
from utils import Utils

chicken_id = '680e477a7d5b06095ef46ad1'
lady_beetles = '6805db0cac48194de3cd407c'
seers = '6805db0cac48194de3cd40b5'

beetles = scs.Team(lady_beetles)
seers = scs.Team(seers)
chicken = scs.Team(chicken_id)


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

chicken_scout_dict = {}

chk_names = chicken.player_names
for player_name in chk_names:
    for position, options in Utils.access_json('player_draft_attributes.json').items():
        for option in options:
            if option['Name'] == player_name:
                chicken_scout_dict[player_name] = option['ScoutingReport']


Utils.write_json('chicken_scout_reports.json',chicken_scout_dict)

# print(seers.players['6807f4114251378d1ace1328'].name)
# print(seers.players['6807f4114251378d1ace1328'].position)

# for playername, id in seers.player_ids.items():
#     print(f'{playername} -- {seers.players[id].simplified_position}')


# TODO: stat lists for simplified_positions, implementing calculations, appending to player data