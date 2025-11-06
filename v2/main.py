from api import APIHandler
import pandas as pd
from io import StringIO
import pprint

if __name__ == '__main__':
    handler = APIHandler()
    chk = handler.get_team()
    liberty = handler.get_league(populate='all')
    print(liberty.size)