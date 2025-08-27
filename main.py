import spicy_chicken_stats as scs
import polars as pl
from utils import Utils

chicken_id = '680e477a7d5b06095ef46ad1'
rides_id = '688847f85cb20f9e396ef60b'
avg_pa_per_game = 3.73

chicken = scs.Team(chicken_id)
poggersdorf = scs.Team('68077beaee9f269dec7251e9')
rides = scs.Team('688847f85cb20f9e396ef60b')
wildcard_team = rides
#wildcard_sample = wildcard_team.players[wildcard_team.player_ids['Edith Leon']]


def position_dfs(team):
    print(Utils.printout_header(team.name,'*~'))
    performance_dfs = team.get_position_df()
    print(Utils.printout_header('Fielding'))
    Utils.print_all_cols(performance_dfs[0])
    print(Utils.printout_header('Hitting'))
    Utils.print_all_cols(performance_dfs[1])
    print(Utils.printout_header('Pitching'))
    Utils.print_all_cols(performance_dfs[2])

position_dfs(wildcard_team)
#position_dfs(times)

# Utils.print_all_rows(chicken.inspect_player(wildcard_sample.name))
# Utils.print_all_rows(chicken.inspect_keyword('convincing'))
#chicken.inspect_all()

# print(Utils.printout_header(wildcard_sample.name,'<>'))
# print(wildcard_sample.position)
# print(f'{wildcard_sample.stats}')
#print(chicken.players[chicken.get_player('Mamie Mitra')['PlayerID']].simplified_position)
#print(chicken.inspect_player('Jacob Decker'))
