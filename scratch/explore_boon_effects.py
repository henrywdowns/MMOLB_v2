import pandas as pd

df = pd.read_csv('/workspaces/MMOLB_v2/boon_effect_exports/Boots May_6841e93ef7b5d3bf791d6ce0_boon_detail_pct.csv')

print(df.sort_values(by='net_impact',ascending=False))