import polars as pl
import pyarrow as pa
import pyarrow.compute as pc
from .league import League
import pandas as pd
import datetime as dt

class Interleague:
    # Example usage: self._lesser_data['attrs'] or self._lesser_data['stats']. These will be Interleague's main exports.
    def __init__(self, lesser_leagues: list = None, greater_leagues: list = None, debug = True):
        self.debug = debug
        if self.debug:
            self.init_start = dt.datetime.now()
            print(f'Interleague object initialization began at {self.init_start}')
        self.lesser_leagues = lesser_leagues
        self.greater_leagues = greater_leagues
        self._lesser_data, self._greater_data = self.compile_data(separate=True)
        if self.debug:
            print(f'Interleague object initialization complete. Elapsed processing time: {dt.datetime.now() - self.init_start}')

    
    def ready_to_fry(self):
        cols = ['team','player','group','category','stat','value','values','team_win_diff']

    def _build_team_maps(self):
        leagues = (self.lesser_leagues or []) + (self.greater_leagues or [])
        names_by_id = {}
        win_diff_by_id = {}
        for lg in leagues:
            for tm in lg.teams:
                names_by_id[tm._id] = tm.name
                try:
                    win_diff_by_id[tm._id] = tm.record['Regular Season']['Wins'] - tm.record['Regular Season']['Losses']
                except Exception:
                    # keep it sparse if record missing
                    pass
        return names_by_id, win_diff_by_id


    def compile_data(self, separate=False):
        if self.debug:
            compile_start = dt.datetime.now()
        lesser = {'attrs': None, 'stats': None}
        greater = {'attrs': None, 'stats': None}

        # --- helper: from list[dict[str, DataFrame]] -> one DataFrame with stat_type ---
        def stack_stats(dicts):
            if not dicts:
                return None
            keys = set.intersection(*(set(d) for d in dicts))
            by_key = {k: pd.concat([d[k] for d in dicts], ignore_index=True) for k in keys}
            stacked = pd.concat(by_key, names=['stat_type']).reset_index(level='stat_type').reset_index(drop=True)
            return stacked

        if self.lesser_leagues:
            lesser_attrs = pd.concat([lg.league_attributes() for lg in self.lesser_leagues], ignore_index=True)
            lesser_stats_dicts = [lg.league_statistics() for lg in self.lesser_leagues]
            lesser_stats = stack_stats(lesser_stats_dicts)

            lesser_attrs['league_type'] = 'Lesser'
            if lesser_stats is not None:
                lesser_stats['league_type'] = 'Lesser'

            lesser['attrs'] = lesser_attrs
            lesser['stats'] = lesser_stats

        if self.greater_leagues:
            greater_attrs = pd.concat([lg.league_attributes() for lg in self.greater_leagues], ignore_index=True)
            greater_stats_dicts = [lg.league_statistics() for lg in self.greater_leagues]
            greater_stats = stack_stats(greater_stats_dicts)

            greater_attrs['league_type'] = 'Greater'
            if greater_stats is not None:
                greater_stats['league_type'] = 'Greater'

            greater['attrs'] = greater_attrs
            greater['stats'] = greater_stats

        if separate:
            return lesser, greater

        combined_attrs = pd.concat(
            [df for df in (lesser['attrs'], greater['attrs']) if df is not None],
            ignore_index=True
        ) if (lesser['attrs'] is not None or greater['attrs'] is not None) else None

        combined_stats = pd.concat(
            [df for df in (lesser['stats'], greater['stats']) if df is not None],
            ignore_index=True
        ) if (lesser['stats'] is not None or greater['stats'] is not None) else None
        if self.debug:
            print(f'Finished compiling interleague data. Processing time: {dt.datetime.now() - compile_start}')
        return {'attrs': combined_attrs, 'stats': combined_stats}