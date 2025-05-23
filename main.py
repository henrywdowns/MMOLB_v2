import spicy_chicken_stats as scs

chicken_id = '680e477a7d5b06095ef46ad1'
lady_beetles = '6805db0cac48194de3cd407c'
seers = '6805db0cac48194de3cd40b5'

beetles = scs.Team(lady_beetles)
seers = scs.Team(seers)

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

# for player in seers.players.values():
#     player.extract_stats()

print(seers.players['6807f4114251378d1ace1328'].name)
print(seers.players['6807f4114251378d1ace1328'].position)

# for playername, id in seers.player_ids.items():
#     print(f'{playername} -- {seers.players[id].simplified_position}')


# TODO: build logic for checking games.json vs running game_data.py method;
# TODO: aggregate appearances into stats
# TODO: stat lists for simplified_positions, implementing calculations, appending to player data