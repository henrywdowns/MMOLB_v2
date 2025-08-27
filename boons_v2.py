import csv
import pprint
from utils import Utils
import pandas as pd


# pull local data for regression results
regression_csvs = {
    'avg': '/workspaces/MMOLB_v2/regression_csvs/batting_avg.csv',
    'era': '/workspaces/MMOLB_v2/regression_csvs/era.csv',
    'fip': '/workspaces/MMOLB_v2/regression_csvs/fip.csv',
    'obp': '/workspaces/MMOLB_v2/regression_csvs/obp.csv',
    'ops': '/workspaces/MMOLB_v2/regression_csvs/obps.csv',
    'slg': '/workspaces/MMOLB_v2/regression_csvs/slg.csv',
    'whip': '/workspaces/MMOLB_v2/regression_csvs/whip.csv'
}

# organize csvs into python-ready datasets
def parse_regression_csvs(
    regression_dict = regression_csvs,
    alpha=0.05,
    coef_col="coefficient",
    pval_col="p_value",
    attr_col="attribute"
):
    results = {}
    for key, csv_path in regression_dict.items():
        df = pd.read_csv(csv_path)
        # Filter significant rows
        sig = df[df[pval_col] < alpha]
        # Build mapping attribute -> coefficient
        attr_map = dict(zip(sig[attr_col], sig[coef_col]))
        # Store under the *key* (e.g., "avg", "era", etc.)
        results[key] = attr_map
    return results

coefficients = parse_regression_csvs()

boons = Utils.access_json('boon_bonuses.json')

results = []

for boon_name, boon_data in boons.items():
    if boon_name == 'Template':
        continue

    boon_dict = {boon_name: {}}
    delta = boon_data['Delta'] / 100.0

    for metric, coefs in coefficients.items():
        plus_total = 0.0
        minus_total = 0.0

        # + stats: increase by +delta
        for stat in boon_data.get('+', []):
            beta = coefs.get(stat, 0.0)
            plus_total += beta * (+delta)

        # - stats: decrease by -delta
        for stat in boon_data.get('-', []):
            beta = coefs.get(stat, 0.0)
            minus_total += beta * (-delta)

        boon_dict[boon_name][metric] = {
            '+': plus_total,
            '-': minus_total,
        }

    results.append(boon_dict)


flattened_rows = []

for entry in results:
    for name, stats in entry.items():
        for metric, values in stats.items():
            flattened_rows.append({
                'name': name,
                'stat': metric,
                'plus': round(values['+'], 3),
                'minus': round(values['-'], 3)
            })


