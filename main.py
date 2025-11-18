from MMOLB import APIHandler, Utils
import pandas as pd
from io import StringIO
import pprint

if __name__ == '__main__':
    handler = APIHandler()
    il = handler.get_all_leagues('lesser',lesser_sample_size=2)
    print(il._lesser_data['stats'].sort_values('team_id'))