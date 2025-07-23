#!/usr/bin/env python3
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors

mode = "Hitting"

def load_data(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)

def main():
    data = load_data('player_attributes.json')
    config = {
        'stat_categories': {
            "Pitching": {
                'DEX': ['Accuracy', 'Control', 'Stuff'],
                'STR': ['Velocity', 'Stamina', 'Rotation'],
                'INT': ['Persuasion', 'Presence'],
                'WIS': ['Guts', 'Defiance']
        },
            "Hitting": {
                'DEX': ['Aiming', 'Contact', 'Vision'],
                'STR': ['Muscle','Lift'],
                'INT': ['Cunning','Selflessness','Discipline'],
                'WIS': ['Wisdom','Insight','Intimidation','Determination']
            }
        }
    }
    
    df = pd.DataFrame.from_dict(
        {player: stats[mode]
         for player, stats in data.items()
         if mode in stats},
        orient='index'
    ).apply(pd.to_numeric, errors='coerce')

    vmin, vmax = df.min().min(), df.max().max()
    
    fig, axes = plt.subplots(
        nrows=2,
        ncols=2,
        figsize=(12, len(df) * 0.8),
        sharey=False
    )
    axes = axes.flatten()
    
    cmap = plt.get_cmap('magma')
    norm = colors.PowerNorm(gamma=0.5, vmin=vmin, vmax=vmax)
    
    for idx, (ax, (title, cols)) in enumerate(zip(axes, config['stat_categories'][mode].items())):
        sub = df[cols]
        im = ax.imshow(sub.values, aspect='auto', cmap=cmap, norm=norm)
        ax.set_title(title)
        
        ax.set_xticks(range(len(cols)))
        ax.set_xticklabels(cols, rotation=45, ha='right')
        
        # always set the full set of yticks...
        ax.set_yticks(range(len(df)))
        # ...but only label them on the left column
        if idx % 2 == 0:
            ax.set_yticklabels(df.index)
            ax.tick_params(axis='y', labelleft=True)
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis='y', labelleft=False)
    
    plt.tight_layout(rect=[0, 0, 0.97, 1])
    fig.colorbar(im, ax=axes.tolist(), label='Metric Value', fraction=0.02, pad=0.02)
    plt.savefig(f'heatmaps/{mode.lower()}_side_by_side.png', dpi=150)
    plt.close()

if __name__ == '__main__':
    main()
