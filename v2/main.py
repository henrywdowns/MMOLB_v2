from api import APIHandler
import pandas as pd
from io import StringIO
import pprint

if __name__ == '__main__':
    handler = APIHandler()
    handler.clear_cache()
    chk = handler.get_team()
    # chk_light = handler.get_league(populate='Spicy Chicken Crunchwraps').get_team('Spicy Chicken Crunchwraps')
    # print(chk.players)
    liberty = handler.get_league(populate='All')
    print(liberty.size)
    print(liberty.get_team('Spicy Chicken Crunchwraps'))
    # print(chk_light.players)