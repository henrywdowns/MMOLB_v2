from MMOLB import APIHandler
import pandas as pd
from io import StringIO
import pprint

if __name__ == '__main__':
    handler = APIHandler()
    chk = handler.get_team()
    chk_league = handler.get_league(populate='Spicy Chicken Crunchwraps')
    chk_light = chk_league.get_team('Spicy Chicken Crunchwraps')

    pprint.pprint(chk.attributes.keys())
    pprint.pprint(chk_light.attributes.keys())