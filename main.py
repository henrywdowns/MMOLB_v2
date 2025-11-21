from MMOLB import APIHandler, Utils, DeepFrier
import pandas as pd
from io import StringIO
import pprint

if __name__ == '__main__':
    handler = APIHandler()
    il = handler.get_all_leagues('lesser',lesser_sample_size=2)
    il_stats = il._lesser_data['stats'].sort_values('team_id')
    il_deepfry = DeepFrier(il,interleague=True)
    print(il_deepfry._attributes_data)
    print(il_deepfry._stats_data)
    