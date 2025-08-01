from utils import Utils
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime as dt

df_att = Utils.access_csv('attributes_db_export_080125_1932.csv').to_pandas()
df_per = Utils.access_csv('performance_db_export_080125_1927.csv').to_pandas()

merged_df = pd.merge(df_att,df_per,left_on='player_id',right_on='inner_id')

print('DFs merged. Sorting into Pitching / Hitting')

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
    "walked", "walked_risp", "caught_stealing", "caught_stealing_risp"
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

# coercing nan values because right now they aren't all being read as NaN for some reason

for col in pitching_attrs + hitting_attrs + pitching_perfs + hitting_perfs:
    merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')

# creating distinct pitching and hitting datasets

pitching_df = merged_df[merged_df['Control'].notna()].copy()
pitching_df = pitching_df[pitching_attrs + pitching_perfs].fillna(0)

hitting_df = merged_df[merged_df['Contact'].notna()].copy()
hitting_df = hitting_df[hitting_attrs + hitting_perfs].fillna(0)

print('Pitching / Hitting DFs in place.')
# data is in place. let's run some regressions haphazardly

def OLS_regression(key_performance: str, attributes: list, data: pd.DataFrame):
    print(f'Running regression on performance metric {key_performance}')
    X = data[attributes]
    y = data[key_performance]

    print(f'X shape: {X.shape}')
    print(f'y shape: {y.shape}')

    from sklearn.linear_model import LinearRegression

    model = LinearRegression()
    model.fit(X,y)

    print(f'Model r-square: {model.score(X,y)}')
    for attr, coef in zip(hitting_attrs, model.coef_):
        print(f'{attr} -> {coef:0.3}')
    
    print('Plotting...')
    import matplotlib.pyplot as plt
    coef_df = pd.DataFrame({
        'attribute': hitting_attrs,
        'coefficient': model.coef_
    }).sort_values(by='coefficient', ascending=False)

    plt.figure(figsize=(10,5))
    plt.barh(coef_df['attribute'], coef_df['coefficient'])
    plt.axvline(0, color='black', linewidth=0.8)
    plt.title(f'Attribute impact on {key_performance.capitalize().replace('_',' ')}')
    plt.xlabel("Coefficient")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f'regression_plots/{key_performance}_{dt.strftime(dt.now(), '%m%d%y_%H%M')}')
    print('Plot saved!')

OLS_regression(key_performance = 'home_runs',attributes = hitting_attrs, data = hitting_df)