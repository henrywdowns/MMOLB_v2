import matplotlib.pyplot as plt
from utils import Utils
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime as dt
import statsmodels.api as sm
import numpy as np


df_att = Utils.access_csv('attributes_db_export_080125_1932.csv').to_pandas()
df_per = Utils.access_csv('performance_db_export_080125_1927.csv').to_pandas()

merged_df = pd.merge(df_att,df_per,left_on='player_id',right_on='inner_id')

print('DFs merged. Sorting into Pitching / Hitting / Baserunning')

# columns I want to analyze in the final regression

hitting_perfs = [
    "at_bats", "at_bats_risp", "doubles", "doubles_risp",
    "flyouts", "flyouts_risp", "force_outs", "force_outs_risp",
    "grounded_into_double_play", "grounded_into_double_play_risp",
    "groundouts", "groundouts_risp", "hit_by_pitch", "hit_by_pitch_risp",
    "home_runs", "home_runs_risp", "lineouts", "lineouts_risp",
    "plate_appearances", "plate_appearances_risp", "popouts", "popouts_risp",
    "reached_on_error", "runs", "runs_batted_in", "runs_batted_in_risp",
    "runs_risp", "singles", "singles_risp", "struck_out", "struck_out_risp",
    "walked", "walked_risp", "caught_stealing", "caught_stealing_risp", "triples"
]

hitting_attrs = [
    "Aiming", "Contact", "Cunning", "Determination", "Discipline",
    "Insight", "Intimidation", "Lift", "Muscle", "Selflessness",
    "Vision", "Wisdom"
]

pitching_perfs = [
    "assists", "assists_risp", "ejected", "errors", "errors_risp",
    "appearances", "batters_faced", "batters_faced_risp", "earned_runs", "earned_runs_risp",
    "hit_batters", "hit_batters_risp", "hits_allowed", "hits_allowed_risp",
    "home_runs_allowed", "home_runs_allowed_risp", "mound_visits", "outs",
    "pitches_thrown", "pitches_thrown_risp", "starts", "strikeouts", "strikeouts_risp",
    "unearned_runs", "unearned_runs_risp", "walks", "walks_risp", "complete_games",
    "wins", "games_finished", "quality_starts", "shutouts"
]

pitching_attrs = [
    "Accuracy", "Control", "Defiance", "Guts", "Persuasion",
    "Presence", "Rotation", "Stamina", "Stuff", "Velocity"
]

baserunning_perfs = [
    "runs", "plate_appearances"
]

baserunning_attrs = [
    "Greed", "Performance","Speed","Stealth"
]

# coercing nan values because right now they aren't all being read as NaN for some reason

for col in pitching_attrs + hitting_attrs + baserunning_attrs + pitching_perfs + hitting_perfs + baserunning_perfs:
    merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')

# creating distinct pitching and hitting datasets

pitching_df = merged_df[merged_df['Control'].notna()].copy()
pitching_df = pitching_df[pitching_attrs + pitching_perfs].fillna(0)

baserunning_df = merged_df[merged_df['Performance'].notna()].copy()
baserunning_df = baserunning_df[baserunning_attrs + baserunning_perfs].fillna(0)

hitting_df = merged_df[merged_df['Contact'].notna()].copy()
hitting_df = hitting_df[hitting_attrs + hitting_perfs].fillna(0)
hitting_df['hits'] = (
    hitting_df['singles'] +
    hitting_df['doubles'] +
    hitting_df['triples'] +
    hitting_df['home_runs'] +
    hitting_df['walked'] +
    hitting_df['hit_by_pitch']
)

obp_denom = hitting_df['at_bats'] + hitting_df['walked'] + hitting_df['hit_by_pitch']
hitting_df['hrs_per_ab'] = hitting_df['home_runs']/hitting_df['at_bats']
hitting_df['obp'] = hitting_df['hits'] / obp_denom.replace(0, pd.NA)

hitting_df['slg'] = (
    hitting_df['singles'] +
    hitting_df['doubles'] * 2 +
    hitting_df['triples'] * 3 +
    hitting_df['home_runs'] * 4
) / hitting_df['at_bats'].replace(0, pd.NA)

pitching_df['innings_pitched'] = pitching_df['outs'] / 3

whip_numer = pitching_df['walks'] + pitching_df['hits_allowed']
whip_denom = pitching_df['innings_pitched'].replace(0, pd.NA)
pitching_df['whip'] = whip_numer / whip_denom

era_numer = pitching_df['earned_runs'] * 9
era_denom = pitching_df['innings_pitched'].replace(0, pd.NA)
pitching_df['era'] = era_numer / era_denom

pitching_df['win_rate'] = pitching_df['wins']/pitching_df['appearances']
pitching_df['mound_visits_per_appearance'] = pitching_df['mound_visits']/pitching_df['appearances']

pitching_df = pitching_df.replace([np.inf, -np.inf], pd.NA)
pitching_df = pitching_df.dropna(subset=['whip', 'era'])

hitting_df['obps'] = hitting_df['obp'] + hitting_df['slg']
hitting_df = hitting_df.replace([np.inf, -np.inf], pd.NA)
hitting_df = hitting_df.dropna(subset=['obps'])

baserunning_df = baserunning_df.replace([np.inf, -np.inf], pd.NA)
baserunning_df = baserunning_df.dropna(subset=['plate_appearances'])
baserunning_df['runs_per_PA'] = baserunning_df['runs'] / baserunning_df['plate_appearances']
baserunning_df = baserunning_df.dropna(subset=['runs_per_PA'] + baserunning_attrs)

print('Pitching / Hitting DFs in place.')
# data is in place. let's run some regressions haphazardly


def OLS_regression(key_performance: str, attributes: list, data: pd.DataFrame, save_fig: bool = False):
    #this one's got confidence outputs is all
    
    print(f'Running regression on performance metric {key_performance}')
    
    X = data[attributes]
    y = data[key_performance]

    # Add intercept
    X = sm.add_constant(X)
    X = X.apply(pd.to_numeric, errors='coerce')
    y = pd.to_numeric(y, errors='coerce')

    model = sm.OLS(y, X).fit()

    # Print full summary (includes p-values, R², etc.)
    print(model.summary())

    # Extract coefficients (excluding constant)
    coef_df = model.params.drop('const').to_frame(name='coefficient')
    coef_df['p_value'] = model.pvalues.drop('const')
    coef_df = coef_df.sort_values(by='coefficient', ascending=False).reset_index()
    coef_df.rename(columns={'index': 'attribute'}, inplace=True)

    # Plot coefficients
    plt.figure(figsize=(10,5))
    plt.barh(coef_df['attribute'], coef_df['coefficient'], color='skyblue')
    plt.axvline(0, color='black', linewidth=0.8)
    plt.title(f'Attribute impact on {key_performance.capitalize().replace("_", " ")}')
    plt.xlabel("Coefficient")
    plt.gca().invert_yaxis()
    
    plt.tight_layout()
    if save_fig:
        filename = f'regression_plots/{key_performance}_{dt.strftime(dt.now(), "%m%d%y_%H%M")}.png'
        plt.savefig(filename)
        print(f'Plot saved to {filename}!')

OLS_regression(key_performance = 'obps',attributes = hitting_attrs, data = hitting_df)
OLS_regression(key_performance = 'obp',attributes = hitting_attrs, data = hitting_df)
OLS_regression(key_performance = 'hrs_per_ab',attributes = hitting_attrs, data = hitting_df)

OLS_regression(key_performance = 'era',attributes = pitching_attrs, data = pitching_df)
OLS_regression(key_performance = 'whip',attributes = pitching_attrs, data = pitching_df)

