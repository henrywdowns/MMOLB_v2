from .league import League
import pandas as pd

class Interleague:
    def __init__(self, lesser_leagues: list = None, greater_leagues: list = None):
        self.lesser_leagues = lesser_leagues
        self.greater_leagues = greater_leagues
        self._lesser_data, self._greater_data = self.compile_data(separate=True)

    def compile_data(self, separate=False):
        lesser = {'attrs': None, 'stats': None}
        greater = {'attrs': None, 'stats': None}

        if self.lesser_leagues:
            attrs_df = pd.concat([lg.league_attributes() for lg in self.lesser_leagues])
            stats_df = pd.concat([lg.league_statistics() for lg in self.lesser_leagues])
            attrs_df['league_type'] = 'Lesser'
            stats_df['league_type'] = 'Lesser'
            lesser['attrs'] = attrs_df
            lesser['stats'] = stats_df

        if self.greater_leagues:
            attrs_df = pd.concat([lg.league_attributes() for lg in self.greater_leagues])
            stats_df = pd.concat([lg.league_statistics() for lg in self.greater_leagues])
            attrs_df['league_type'] = 'Greater'
            stats_df['league_type'] = 'Greater'
            greater['attrs'] = attrs_df
            greater['stats'] = stats_df

        if separate:
            return lesser, greater

        # If not separate, combine everything into single DataFrames
        combined_attrs = pd.concat(
            [df for df in [lesser['attrs'], greater['attrs']] if df is not None],
            ignore_index=True
        )
        combined_stats = pd.concat(
            [df for df in [lesser['stats'], greater['stats']] if df is not None],
            ignore_index=True
        )

        return {
            'attrs': combined_attrs,
            'stats': combined_stats
        }
