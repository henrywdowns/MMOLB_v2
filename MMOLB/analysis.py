import pandas as pd

class DeepFrier:
    def __init__(self,filename):
        self._filename = filename
        self._data = pd.read_csv(self._filename)

    def summarize_league_attrs(self):
        # take in the league-level player attrs and identify trends
        
        df = self._data.pivot_table(
            index=['category','stat'],
            values='value',
            aggfunc='mean'
        ).reset_index()

        return df
    
    def describe_attr_categories(self):
        df = self._data
        outputs = {}
        categories = list(df['category'].unique())
        for cat in categories:
            cat_filter = df[df['category'] == cat]
            outputs[cat] = cat_filter.describe()
        return outputs