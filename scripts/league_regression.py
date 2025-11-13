import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MMOLB import APIHandler, DeepFrier

handler = APIHandler()
liberty = handler.get_league(populate='all')
frier = DeepFrier(liberty)
# model = frier.attrs_regression('batting',dependent_variable='OBP',sm_summary=True,detailed_output=True)
# print(model['summary_text'])
# inters = frier.attrs_interaction('batting','OBP',['Insight','Determination','Discipline','Vision'])
# print(inters)
print([(k, v.describe()) for k,v in (frier._stats_data.items())])