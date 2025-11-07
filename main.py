from MMOLB import APIHandler
import pandas as pd
from io import StringIO
import pprint

if __name__ == '__main__':
    handler = APIHandler()
    chk = handler.get_team()
    chk_league = handler.get_league(populate='Spicy Chicken Crunchwraps')
    chk_light = chk_league.get_team('Spicy Chicken Crunchwraps')
    chk_stats = chk.run_stats(truncate=True)
    # chk_pitching = chk_stats.get('pitching')
    # chk_pitching.to_csv('v2/df_outputs/chk_pitching_stats.csv')
    # df = pd.read_csv('v2/df_outputs/chk_pitching_stats.csv')
    print(chk_stats['hitting'].describe())