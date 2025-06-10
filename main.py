import spicy_chicken_stats as scs
import polars as pl
from utils import Utils

chicken_id = '680e477a7d5b06095ef46ad1'
lady_beetles = '6805db0cac48194de3cd407c'
seers = '6805db0cac48194de3cd40b5'

# beetles = scs.Team(lady_beetles)
# seers = scs.Team(seers)
chicken = scs.Team(chicken_id)

# sample_players = {
#     'kibbles_swift':seers.players[seers.player_ids['Kibbles Swift']],
#     'taylor_mogensen':seers.players[seers.player_ids['Taylor Mogensen']],
#     'fizz_kaneko':seers.players[seers.player_ids['Fizz Kaneko']],
#     'null_baba':seers.players[seers.player_ids['Null Baba']]
#     }

wildcard_team = chicken
wildcard_sample = wildcard_team.players[wildcard_team.player_ids['Daniel Breen']]

pitching_df = chicken.get_position_df(position='pitching')
Utils.print_all_cols(pitching_df)

print(Utils.printout_header(wildcard_sample.name,'<>'))
print(f'{wildcard_sample.stats}')

# print(Utils.access_csv('team_rankings.csv'))


# TODO: stat lists for simplified_positions, implementing calculations, appending to player data