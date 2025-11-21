import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MMOLB import APIHandler, Utils, DeepFrier
import pandas as pd
from io import StringIO
import pprint


handler = APIHandler()
il = handler.get_all_leagues()
fry = DeepFrier(il,interleague=True)

fip_reg = fry.attrs_regression('hitting','OPS',sm_summary=True,detailed_output=True)

print(fry.reorder_regression_coefs(fip_reg['sm_results']))