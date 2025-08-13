import csv
import pprint
from utils import Utils
import pandas as pd

coefficients = {
    "whip": {
        "stat": "WHIP",
        "const": 2.175,
        "Accuracy": -0.0206,
        "Control": -0.0534,
        "Persuasion": -0.0318,
        "Presence": -0.0205,
        "Rotation": -0.0219,
        "Stuff": -0.0381,
        "Velocity": -0.0497
    },
    "era": {
        "stat": "ERA",
        "const": 8.6221,
        #"Accuracy": 0.0704,
        "Control": -0.1962,
        "Defiance": -0.0120,
        "Persuasion": -0.1544,
        "Presence": -0.1499,
        "Rotation": -0.2213,
        "Stamina": -0.1380,
        "Stuff": -0.2486,
        "Velocity": -0.219
    },
    "ops": {
        "stat": "OPS",
        "const": 0.5610,
        "Aiming": 0.0161,
        "Contact": 0.0148,
        #"Cunning": 0.0057,
        #"Determination": 0.0029,
        "Discipline": 0.0077,
        #"Insight": 0.0048,
        #"Intimidation": 0.0063,
        "Lift": 0.0107,
        "Muscle": 0.0213,
        #"Selflessness": -3.439e-05,
        #"Vision": -0.0018,
        #"Wisdom": 0.0060,
    },
    "obp": {
        "stat": "OBP",
        "const": 0.2935,
        "Aiming": 0.0065,
        #"Contact": 0.0003,
        #"Cunning": 0.0024,
        "Determination": 0.0031,
        "Discipline": 0.0080,
        #"Insight": 0.0021,
        "Intimidation": 0.0032,
        #"Lift": 0.0002,
        "Muscle": 0.0035,
        #"Selflessness": -0.0002,
        #"Vision": -0.0015,
        #"Wisdom": 0.0008,
    },
    "hrs_per_ab": {
        "stat": "HRs_per_AB",
        "const": 0.0150,
        #"Aiming": 0.1234,
        "Contact": 0.002,
        #"Cunning": 0.1178,
        #"Determination": -0.0556,
        #"Discipline": -0.1257,
        #"Insight": 0.1110,
        #"Intimidation": 0.0606,
        "Lift": 0.0024,
        "Muscle": 0.0035,
        #"Selflessness": 0.0813,
        #"Vision": 0.1549,
        #"Wisdom": 0.1167,
    }
}
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


# flattened_rows = []

# for entry in results:
#     for name, stats in entry.items():
#         for metric, values in stats.items():
#             flattened_rows.append({
#                 'name': name,
#                 'stat': metric,
#                 'plus': round(values['+'], 3),
#                 'minus': round(values['-'], 3)
#             })

# csv_path = 'boon_bonuses.csv'
# with open(csv_path, 'w', newline='') as f:
#     writer = csv.DictWriter(f, fieldnames=['name', 'stat', 'plus', 'minus'])
#     writer.writeheader()
#     writer.writerows(flattened_rows)

# csv_path


df = pd.read_csv('boon_bonuses.csv')
df['net_impact'] = df['plus'] - df['minus']
df = df.sort_values(by=["name","net_impact"],ascending=False)
print(df)

print(df[df['stat']=='whip'])