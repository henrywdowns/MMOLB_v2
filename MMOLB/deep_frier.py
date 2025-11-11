import pandas as pd
import functools
import statsmodels.api as sm

class DeepFrier:
    def __init__(self,league,filename=None,diff_threshold=None):
        self._filename = filename
        self._attributes_data: pd.DataFrame = league.league_attributes()
        self._stats_data: pd.DataFrame = league.league_statistics()
        self.league = league
        self.diff_threshold = diff_threshold

    def summarize_league_attrs(self,diff_threshold=None) -> pd.DataFrame:
        # take in the league-level player attrs and identify trends
        df = self._data.pivot_table(
            index=['category','stat','team_win_diff'],
            values='value',
            aggfunc='mean'
        ).reset_index()
        diff_threshold = diff_threshold if diff_threshold else self.diff_threshold # I know this looks insane. Just a little flexibility to set it for the class and method
        if diff_threshold:
            try:
                df = df[df['team_win_diff']>diff_threshold]
            except:
                print(df.columns)
        return df
    
    def describe_attr_categories(self) -> dict:
        df = self.attributes_data
        outputs = {}
        categories = list(df['category'].unique())
        for cat in categories:
            cat_filter = df[df['category'] == cat]
            outputs[cat] = cat_filter.describe()
        
        return outputs
    
    def _cat_stat_dict(self,df):
        return {category: list(set(df.loc[df['category'] == category, 'stat'])) for category in df['category'].unique()}


    def with_sm_summary(method):
        # decorator: if user passes sm_summary=True, attach statsmodels OLS results.
        @functools.wraps(method)
        def wrapper(self, *args, sm_summary: bool = False, detailed_output = False, **kwargs):
            out = method(self, *args, **kwargs)

            if not sm_summary:
                return out

            X_train = out["X_train"]
            y_train = out["y_train"]

            X_train_const = sm.add_constant(X_train, has_constant='add')
            res = sm.OLS(y_train, X_train_const).fit()

            out["sm_results"] = res
            out["summary_text"] = res.summary().as_text()
            return out if detailed_output else out['sm_results'].summary()
        return wrapper

    @with_sm_summary
    def attrs_regression(self, category, dependent_variable: str, independent_variables: list = [], scope='total', league_obj=None):
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split
        
        match category.lower(): # account for generally interchangeable baseball terminology
            case 'batting'|'hitting':
                category = 'hitting'
            case _:
                category = category.lower()
        
        if not league_obj: # allows user to specify new league, but has a default fallback for ease of use
            league_obj = self.league
        
        # utility thingy to automate independent variables in argument for ease of use
        attrs_df: pd.DataFrame = self._attributes_data
        if not independent_variables:
            independent_variables = self._cat_stat_dict(attrs_df)

        # at long last we start extracting and transforming data from League object
        stats_df = self._stats_data[category]
        attrs_filter = attrs_df[(attrs_df['category'].str.lower() == category) & (attrs_df['group'] == scope)]

        # need to re-pivot the attrs_df to make stat column's values into columns
        attrs_piv = attrs_filter.pivot_table(
            index=['team','player','group','category','team_win_diff'],
            columns='stat',
            values='value'
        ).reset_index()

        merged_df = attrs_piv.merge(stats_df,left_on=['player','team'],right_on=['player_name','team_name'])

        # I'll try regressing, that's a good trick
        X = merged_df[independent_variables[category.capitalize()]]
        y = merged_df[dependent_variable]

        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=4)
        model = LinearRegression()
        model.fit(X_train,y_train)
        # wait it's done?

        # yes
        return {
            "model": model,
            "X_train": X_train, "y_train": y_train,
            "X_test": X_test,   "y_test": y_test,
            "features": list(X.columns)
        }
    
    