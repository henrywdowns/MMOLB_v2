import sys, os
import pprint
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MMOLB import APIHandler, DeepFrier

handler = APIHandler()
il = handler.get_all_leagues(scope='lesser')
frier = DeepFrier(il,interleague=True)

batting_kpis = frier.attrs_regression('batting','team_win_diff',['SB%','BB%','K%','BA','ISO'],sm_summary=True,detailed_output=True)
pitching_kpis = frier.attrs_regression('pitching','team_win_diff',['BB9','H9','K9','HR9'],sm_summary=True,detailed_output=True)
print(frier.reorder_regression_coefs(batting_kpis['sm_results']))
print(frier.reorder_regression_coefs(pitching_kpis['sm_results']))

print(batting_kpis['summary_text'])
print(pitching_kpis['summary_text'])

# batting_inters = frier.interaction_regression('batting','team_win_diff',sm_summary=True,detailed_output=True)
# pitching_inters = frier.interaction_regression('pitching','team_win_diff',sm_summary=True,detailed_output=True)

# for x in [batting_inters,pitching_inters]:
#     frier.reorder_regression_coefs(x['sm_results'])