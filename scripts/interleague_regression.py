import sys, os
import pprint
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MMOLB import APIHandler, DeepFrier

handler = APIHandler()
il = handler.get_all_leagues(scope='lesser')
frier = DeepFrier(il,interleague=True)

batting_kpis = frier.attrs_regression('batting','team_win_diff',['SB%','BB%','K%','BA','ISO'],sm_summary=True,detailed_output=True)
pitching_kpis = frier.attrs_regression('pitching','team_win_diff',['BB9','H9','K9','HR9'],sm_summary=True,detailed_output=True)

# high ranking batting_kpis
iso = frier.attrs_regression('batting','ISO',sm_summary=True,detailed_output=True)
bb = frier.attrs_regression('batting','BB%',sm_summary=True,detailed_output=True)
babip = frier.attrs_regression('batting','BABIP',sm_summary=True,detailed_output=True)

# high ranking pitching_kpis
k9 = frier.attrs_regression('pitching','K9',sm_summary=True,detailed_output=True)
bb9 = frier.attrs_regression('pitching','BB9',sm_summary=True,detailed_output=True)

roundup = [batting_kpis,iso,bb,pitching_kpis,k9,bb9]

for reg in roundup:
    print(frier.reorder_regression_coefs(reg['sm_results']))
    print(reg['summary_text'])

# batting_inters = frier.interaction_regression('batting','team_win_diff',sm_summary=True,detailed_output=True)
# pitching_inters = frier.interaction_regression('pitching','team_win_diff',sm_summary=True,detailed_output=True)

# for x in [batting_inters,pitching_inters]:
#     frier.reorder_regression_coefs(x['sm_results'])