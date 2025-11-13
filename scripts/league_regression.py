import sys, os
import pprint
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MMOLB import APIHandler, DeepFrier

handler = APIHandler()
liberty = handler.get_league(populate='all')
frier = DeepFrier(liberty)
model = frier.interaction_regression('batting',dependent_variable='OBP',interaction_variables=['Determination','Discipline'],sm_summary=True,detailed_output=True)
summary = model['summary_text']

print(frier.reorder_regression_coefs(model['sm_results']))
# inters = frier.attrs_interaction('batting','OBP',['Insight','Determination','Discipline','Vision'])
# print(frier.attrs_hypotheticals('batting','OBP'))
