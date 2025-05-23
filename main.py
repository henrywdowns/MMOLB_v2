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

# kibbles_swift = seers.players[seers.player_ids['Kibbles Swift']]
# print(kibbles_swift.simplified_position)
# print(kibbles_swift.stats)

seers.get_game_history()
seers.game_log.get_appearances()


# TODO: build logic for checking games.json vs running game_data.py method;
# TODO: aggregate appearances into stats
# TODO: stat lists for simplified_positions, implementing calculations, appending to player data