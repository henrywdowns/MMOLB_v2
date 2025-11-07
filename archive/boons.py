import csv
import pprint
from utils import Utils
import pandas as pd
import spicy_chicken_stats as scs

chicken_id = '680e477a7d5b06095ef46ad1'
dogs_id = '688847f85cb20f9e396ef60b'

regression_csvs = {
    'avg': '/workspaces/MMOLB_v2/regression_csvs/batting_avg.csv',
    'era': '/workspaces/MMOLB_v2/regression_csvs/era.csv',
    'fip': '/workspaces/MMOLB_v2/regression_csvs/fip.csv',
    'obp': '/workspaces/MMOLB_v2/regression_csvs/obp.csv',
    'ops': '/workspaces/MMOLB_v2/regression_csvs/obps.csv',  # fixed
    'slg': '/workspaces/MMOLB_v2/regression_csvs/slg.csv',
    'whip': '/workspaces/MMOLB_v2/regression_csvs/whip.csv'
}

def get_player_data(team_id: str):
    team_obj = scs.Team(team_id)
    return {p.player_id: p.name for p in team_obj.players.values()}

def parse_regression_csvs(
    regression_dict = regression_csvs,
    alpha=0.05,
    coef_col="coefficient",
    pval_col="p_value",
    attr_col="attribute"
):
    """
    Returns:
      coefficients: {metric: {attribute: beta}  # only significant rows}
      intercepts:   {metric: const or None}     # const captured regardless of significance
    """
    coefficients = {}
    intercepts = {}
    for key, csv_path in regression_dict.items():
        df = pd.read_csv(csv_path)

        # capture intercept regardless of significance
        const_mask = df[attr_col].astype(str).str.lower().eq('const')
        if const_mask.any():
            intercepts[key] = float(df.loc[const_mask, coef_col].iloc[0])
        else:
            intercepts[key] = None

        # keep only significant rows for the attribute->coef map
        sig = df[df[pval_col] < alpha]
        coefficients[key] = dict(zip(sig[attr_col], sig[coef_col]))
    return coefficients, intercepts

def player_boon_effects(team_id, boon_choice=None, export=True):
    team_obj = scs.Team(team_id)
    player_dict = get_player_data(team_id)
    coefficients, intercepts = parse_regression_csvs()
    attrs = Utils.access_json('attributes_db.json')

    # load boons once, then optionally narrow
    all_boons = Utils.access_json('boon_bonuses.json')
    if boon_choice:
        if boon_choice not in all_boons:
            raise ValueError(f"Boon '{boon_choice}' not found in boon_bonuses.json")
        boons = {boon_choice: all_boons[boon_choice]}
    else:
        boons = all_boons

    results = []

    for boon_name, boon_data in boons.items():
        if boon_name == 'Template':
            continue

        boon_dict = {boon_name: {}}
        delta = float(boon_data['Delta']) / 100.0

        for player_id, player_name in player_dict.items():
            # resolve player attrs safely
            _team_block = attrs.get(team_id, {})
            if isinstance(_team_block, list):
                _entry = next((p for p in _team_block if player_id in p), None)
                player_attrs = {} if _entry is None else _entry[player_id]
            else:
                player_attrs = _team_block.get(player_id, {})

            scs_player = team_obj.players[player_id]
            simplified = scs_player.simplified_position
            pos_category = 'Pitching' if simplified == 'Pitcher' else 'Batting'

            player_stats = (player_attrs.get(pos_category) or {})
            # collect all metrics for this player without overwriting on each metric
            per_metric = {}

            for metric, coefs in coefficients.items():
                plus_total = 0.0
                minus_total = 0.0

                # + stats: increase by +delta
                for stat in boon_data.get('+', []):
                    beta = coefs.get(stat, 0.0)
                    x = player_stats.get(stat, 0.0)
                    plus_total += beta * x * (+delta)

                # - stats: decrease by -delta
                for stat in boon_data.get('-', []):
                    beta = coefs.get(stat, 0.0)
                    x = player_stats.get(stat, 0.0)
                    minus_total += beta * x * (-delta)

                per_metric[metric] = {'+': plus_total, '-': minus_total}

            boon_dict[boon_name][player_name] = per_metric

        results.append(boon_dict)

    # flatten
    flattened_rows = []
    for boon_dict in results:
        for name, players in boon_dict.items():
            for player_name, metrics in players.items():
                for metric, values in metrics.items():
                    flattened_rows.append({
                        'player': player_name,
                        'name': name,
                        'stat': metric,
                        'plus': round(values['+'], 3),
                        'minus': round(values['-'], 3)
                    })

    csv_path = 'boon_bonuses.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['player', 'name', 'stat', 'plus', 'minus'],
        )
        writer.writeheader()
        writer.writerows(flattened_rows)

    # analysis dataframe
    df = pd.read_csv(csv_path)
    df['net_impact'] = df['plus'] + df['minus']

    # map intercepts (may be None)
    df['intercept'] = df['stat'].map(intercepts)

    # safe pct calculation
    def pct(row):
        b = row['intercept']
        if b is None or b == 0:
            return None
        return round((row['net_impact'] / b) * 100, 2)

    df['pct_impact'] = df.apply(pct, axis=1)

    df = df.sort_values(by=["net_impact", "name"], ascending=False)

    # pretty prints (low-is-better ascending for these)
    low_is_better = {'whip', 'era', 'fip'}  # fixed comma bug
    for stat in ['obp', 'ops', 'slg', 'fip', 'whip', 'era']:
        asc = (stat in low_is_better)
        print(Utils.printout_header(stat.upper()))
        output_df = df[df['stat'] == stat].sort_values(by='net_impact', ascending=asc)
        print(output_df)
        if export:
            filename = f'boon_effect_exports/{stat}_export.csv'
            output_df.to_csv(filename,index=False)

if __name__ == '__main__':
    player_boon_effects(dogs_id,"Archer's Mark")
