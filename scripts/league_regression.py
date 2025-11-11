import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MMOLB import APIHandler, DeepFrier

handler = APIHandler()
liberty = handler.get_league(populate='all')
frier = DeepFrier(liberty)
model = frier.attrs_regression('pitching',dependent_variable='FIP',sm_summary=True,detailed_output=True)
# print(model)


print(model['summary_text'])