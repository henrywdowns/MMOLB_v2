import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MMOLB import APIHandler, Utils
import pandas as pd
from io import StringIO
import pprint

if __name__ == '__main__':
    handler = APIHandler()
    liberty = handler.get_league(populate='all')
    chk = handler.get_team()
    chk_light = liberty.get_team('Spicy Chicken Crunchwraps')
    df = liberty.league_attributes()
    df.to_csv(Utils.date_filename('df_outputs/League_Attrs.csv'),index=False)
    print(df.head())
    print(df.describe())