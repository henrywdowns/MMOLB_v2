from api import APIHandler
import pandas as pd
from io import StringIO
import pprint

if __name__ == '__main__':
    handler = APIHandler()
    chk = handler.get_team()
    chk_league = handler.get_league(populate='Spicy Chicken Crunchwraps')
    chk_light = chk_league.get_team('Spicy Chicken Crunchwraps')
    league_performance = chk_league.league_statistics()
    hitting_df = league_performance['hitting'].sort_values(['team_name','player_name'],ascending=True,axis=0)
    pitching_df = league_performance['pitching'].sort_values(['team_name','player_name'],ascending=True,axis=0)