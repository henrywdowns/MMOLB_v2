import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MMOLB import APIHandler, Utils, DeepFrier
import pandas as pd
from io import StringIO
import pprint

handler = APIHandler()
chk = DeepFrier('df_outputs/20251110_League_Attrs.csv',diff_threshold=30)

print(chk.summarize_league_attrs().sort_values(['category','value'],ascending=False))


print(chk.describe_attr_categories())