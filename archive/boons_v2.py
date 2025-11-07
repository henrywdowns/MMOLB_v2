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

# Which metrics are lower-is-better (we'll flip their sign for scoring)
LOW_IS_BETTER = {'whip', 'era', 'fip'}

def _resolve_player_attrs(attrs, team_id, player_id):
    """
    Handles both dict and list shapes in attributes_db.json for a single player.
    Returns the player's per-category attributes dict (e.g., {'Batting': {...}, 'Pitching': {...}})
    or {} if not found.
    """
    _team_block = attrs.get(team_id, {})
    if isinstance(_team_block, list):
        _entry = next((p for p in _team_block if player_id in p), None)
        return {} if _entry is None else _entry[player_id]
    return _team_block.get(player_id, {}) or {}

def _pos_category(team_obj, player_id):
    scs_player = team_obj.players[player_id]
    return 'Pitching' if scs_player.simplified_position == 'Pitcher' else 'Batting'

def best_boons_for_player(
    team_id: str,
    player_id: str,
    *,
    objective: str = "pct",
    weights: dict | None = None,
    export: bool = True,
    export_dir: str = "boon_effect_exports",
    top_n: int = 10,
):
    """
    Evaluate ALL boons for a specific player and rank them.

    Args:
      team_id: team (e.g., dogs_id)
      player_id: the player's id within that team
      objective: "pct" (default) to sum signed pct impacts, or "raw" to sum signed net impacts
      weights: optional per-metric weights, e.g. {"ops": 2.0, "slg": 1.0, "era": 1.5}
      export: write two CSVs: detailed rows and aggregated ranking
      export_dir: directory to write CSVs into
      top_n: how many top rows to print (ranking preview)

    Returns:
      detail_df: each (boon, stat) row for the player with net & pct impacts and signed values
      ranking_df: one row per boon with total score, sorted descending
    """
    import os
    from collections import defaultdict

    team_obj = scs.Team(team_id)
    player_lookup = get_player_data(team_id)
    player_name = player_lookup.get(player_id, player_id)

    coefficients, intercepts = parse_regression_csvs()
    attrs = Utils.access_json('attributes_db.json')
    all_boons = Utils.access_json('boon_bonuses.json')

    # resolve player attributes & category
    player_attr_block = _resolve_player_attrs(attrs, team_id, player_id)
    pos_category = _pos_category(team_obj, player_id)
    player_stats = player_attr_block.get(pos_category, {}) or {}

    # ensure weights default to 1.0 per metric if provided partially
    weights = weights or {}
    def w(metric): return float(weights.get(metric, 1.0))

    # Prepare detailed rows
    detailed_rows = []
    for boon_name, boon_data in all_boons.items():
        if boon_name == "Template":
            continue
        # normalize delta to fraction
        try:
            delta = float(boon_data['Delta']) / 100.0
        except Exception:
            # If malformed, skip safely
            continue

        # Compute per-metric effects (same approach as player_boon_effects)
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

            net = plus_total + minus_total
            b0 = intercepts.get(metric)  # may be None
            if b0 is None or b0 == 0:
                pct = None
            else:
                pct = round((net / b0) * 100, 4)

            # direction: metrics where lower is better get negative sign for scoring
            direction = -1.0 if metric in LOW_IS_BETTER else +1.0

            detailed_rows.append({
                'player_id': player_id,
                'player': player_name,
                'boon': boon_name,
                'stat': metric,
                'plus': round(plus_total, 6),
                'minus': round(minus_total, 6),
                'net_impact': round(net, 6),
                'intercept': b0 if (b0 is None) else float(b0),
                'pct_impact': pct,                      # may be None
                'direction': direction,
                'weight': w(metric),
                'signed_net': round(net * direction * w(metric), 6),
                'signed_pct': (None if pct is None else round(pct * direction * w(metric), 6)),
            })

    import pandas as pd
    detail_df = pd.DataFrame(detailed_rows)

    if detail_df.empty:
        print(f"No data generated for player {player_name} ({player_id}). Check attributes/boons/regressions.")
        return detail_df, pd.DataFrame()

    # Aggregate to boon-level scores
    if objective.lower() == "pct":
        # treat None pct as 0 for aggregation
        detail_df['signed_pct_filled'] = detail_df['signed_pct'].fillna(0.0)
        agg = detail_df.groupby('boon', as_index=False)['signed_pct_filled'].sum().rename(columns={'signed_pct_filled': 'score'})
        objective_used = "pct"
    else:
        agg = detail_df.groupby('boon', as_index=False)['signed_net'].sum().rename(columns={'signed_net': 'score'})
        objective_used = "raw"

    # Also keep a quick view of per-metric contributions for transparency
    contrib = (detail_df.assign(contrib=lambda d:
                                d['signed_pct'].fillna(0.0) if objective_used == "pct" else d['signed_net'])
               .groupby(['boon', 'stat'], as_index=False)['contrib'].sum()
               .sort_values(['boon', 'contrib'], ascending=[True, False]))

    ranking_df = (agg.sort_values('score', ascending=False)
                    .reset_index(drop=True)
                    .assign(rank=lambda d: d.index + 1))

    # Preview top N
    print(Utils.printout_header(f"BEST BOONS FOR {player_name} ({player_id}) — objective={objective_used.upper()}"))
    print(ranking_df.head(top_n))

    # Optional exports
    if export:
        os.makedirs(export_dir, exist_ok=True)
        detail_path = os.path.join(export_dir, f"{player_name}_{player_id}_boon_detail_{objective_used}.csv")
        rank_path = os.path.join(export_dir, f"{player_name}_{player_id}_boon_ranking_{objective_used}.csv")
        contrib_path = os.path.join(export_dir, f"{player_name}_{player_id}_metric_contrib_{objective_used}.csv")
        detail_df.to_csv(detail_path, index=False)
        ranking_df.to_csv(rank_path, index=False)
        contrib.to_csv(contrib_path, index=False)
        print(f"Exported:\n  {detail_path}\n  {rank_path}\n  {contrib_path}")

    return detail_df, ranking_df

if __name__ == '__main__':
    player_boon_effects(dogs_id,"Demonic")
    best_boons_for_player(dogs_id,'68884a23ea7acc171a96890e',export=False)