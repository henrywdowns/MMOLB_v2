#!/usr/bin/env python3
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors

def load_data(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)

def plot_metrics(data: dict) -> None:
    """
    For each top‐level category (Pitching, Hitting, Defense, …),
    build a DataFrame, coerce non‐numeric values to NaN, and plot a heatmap.
    """
    # Gather all categories present in any player
    categories = sorted({cat for player in data.values() for cat in player})
    all_vals = []
    for p in data.values():
        for cat_stats in p.values():
            all_vals.extend(pd.to_numeric(pd.Series(cat_stats), errors='coerce').dropna().tolist())
    vmin, vmax = min(all_vals), max(all_vals)

    for category in categories:
        # Build DataFrame: rows=players, cols=metrics
        df = pd.DataFrame.from_dict(
            {player: stats[category]
             for player, stats in data.items()
             if category in stats},
            orient='index'
        )
        # Convert '?' or other non‐numeric to NaN
        df = df.apply(pd.to_numeric, errors='coerce')
        cmap = plt.get_cmap('magma')
        norm = colors.PowerNorm(gamma=0.5)
        # Plot
        plt.figure(figsize=(10, max(4, len(df) * 0.5)))
        plt.title(f'{category} Metrics Heatmap')
        plt.imshow(df.values,
                    aspect='auto',
                    cmap=cmap,
                    vmin=vmin,
                    # norm=norm,
                    vmax=vmax
                    )
        plt.xticks(range(len(df.columns)), df.columns, rotation=45, ha='right')
        plt.yticks(range(len(df.index)), df.index)
        plt.colorbar(label='Metric Value')
        plt.tight_layout()
    
    # Show all figures at once
    out_fn = f'heatmaps/{category.lower()}_heatmap.png'
    plt.savefig(out_fn, dpi=150)
    plt.close()

def main():
    # Assumes your JSON is saved as metrics.json in the same folder
    data = load_data('player_attributes.json')
    plot_metrics(data)

if __name__ == '__main__':
    main()
