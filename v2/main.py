from api import APIHandler
import pandas as pd
from io import StringIO

if __name__ == '__main__':
    handler = APIHandler()
    chk = handler.get_team()
    robin = chk.get_player('Robin Stoica')
    robin.help()
    print(handler.fc_team_stats)
    chk.run_stats()