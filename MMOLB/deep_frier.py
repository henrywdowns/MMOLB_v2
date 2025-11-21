import pandas as pd
import polars as pl
import functools
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import datetime as dt

class DeepFrier:
    def __init__(self,league,diff_threshold=None,interleague=False,debug=True) -> None:
        self.debug = debug
        if self.debug:
            self.init_start = dt.datetime.now()
            print(f'DeepFrier initializion began at {self.init_start}')
        self.league = league
        if interleague:
            # interleague objects carry their data a little differently.
            attrs_list = []
            stats_list = []
            if getattr(league, "lesser_leagues", None):
                attrs_list.append(league._lesser_data["attrs"])
                stats_list.append(league._lesser_data["stats"])

            if getattr(league, "greater_leagues", None):
                attrs_list.append(league._greater_data["attrs"])
                stats_list.append(league._greater_data["stats"])

            self._attributes_data = pd.concat(attrs_list, ignore_index=True)
            self._stats_data = {k:v for k,v in  pd.concat(stats_list, ignore_index=True).groupby('stat_type')}
        else:
            self._attributes_data: pd.DataFrame = league.league_attributes()
            self._stats_data: pd.DataFrame = league.league_statistics()
        self.diff_threshold = diff_threshold

        if self.debug: 
            print(f'DeepFrier initialized. Elapsed time: {dt.datetime.now()-self.init_start}')

    def _prepare_data(self, category, dependent_variable, independent_variables, scope, league_obj, merged_df_inject = None):
        if merged_df_inject is None: # skip data extraction and transformation if passing in a merged df. assumes injection is already properly prepared.
            # default to class attributes
            if not league_obj: league_obj = self.league
            attrs_df = self._attributes_data

            # account for commonly interchangeable terminology
            match category.lower():
                case 'batting' | 'hitting':
                    category = 'batting'
                case _:
                    category = category.lower()        

            # include all attributes in category by default, filter both datasets by category, filter by attributes scope (total, base, or equip)
            if not independent_variables:
                independent_variables = self._cat_stat_dict(attrs_df)[category.capitalize()]
            stats_df = self._stats_data[category]
            attrs_filter = attrs_df[(attrs_df['category'].str.lower()==category) & (attrs_df['group']==scope)]
            
            # pivot attrs data to give each independent variable its own col
            attrs_piv = attrs_filter.pivot_table(
                index=['team','player','group','category','team_win_diff','position_type'],
                columns='stat', values='value'
            ).reset_index()

            # inner join
            merged_df = attrs_piv.merge(stats_df.drop(columns='team_win_diff'),left_on=['player','team'],right_on=['player_name','team_name'])
            if category == 'batting':
                merged_df = merged_df[merged_df['position_type'] == 'Batter']
            elif category == 'pitching':
                merged_df = merged_df[merged_df['position_type'] == 'Pitcher']
        else:
            merged_df = merged_df_inject
        print(merged_df.columns)
        merged_df = merged_df.dropna(subset=[dependent_variable])
        X = merged_df[independent_variables]
        y = merged_df[dependent_variable]
        return merged_df, X, y

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
    
    def _cat_stat_dict(self,df) -> dict:
        # mainly for attrs. input data, output dict of all attribute names
        return {category: list(set(df.loc[df['category'] == category, 'stat'])) for category in df['category'].unique()}


    def with_sm_summary(method):
        import numpy as np
        @functools.wraps(method)
        def wrapper(self, *args, sm_summary: bool = False, detailed_output=False, **kwargs):
            out = method(self, *args, **kwargs)
            if not sm_summary:
                return out

            X_train = out["X_train"]
            y_train = out["y_train"]
            model = out.get("model", None)

            # Use pipeline preprocessing but KEEP column names
            Xt = X_train.copy()
            if isinstance(model, Pipeline):
                # apply all steps except final estimator
                steps = list(model.named_steps.items())[:-1]
                for _, step in steps:
                    Xt = step.transform(Xt)
            else:
                Xt = Xt.apply(pd.to_numeric, errors="coerce").to_numpy()

            # ---> IMPORTANT: restore names <---
            if isinstance(Xt, np.ndarray):
                Xt = pd.DataFrame(Xt, columns=X_train.columns, index=X_train.index)

            # y as 1D float Series aligned to X
            y = pd.to_numeric(getattr(y_train, "squeeze", lambda: y_train)(), errors="coerce")
            mask = y.notna() & Xt.notna().all(axis=1)
            X_named = Xt.loc[mask].astype(float)
            y_named = y.loc[mask].astype(float)

            # Now statsmodels will keep ['const', *feature names]
            X_const = sm.add_constant(X_named, has_constant="add")
            res = sm.OLS(y_named, X_const).fit(cov_type="HC3")

            out["sm_results"] = res
            out["summary_text"] = res.summary().as_text()
            return out if detailed_output else out["sm_results"].summary()
        return wrapper


    @with_sm_summary
    def attrs_regression(self, category, dependent_variable: str, independent_variables: list = [], scope='total'):
        reg_start = dt.datetime.now()
        merged_df, X, y = self._prepare_data(category, dependent_variable, independent_variables, league_obj=self.league,scope=scope)

        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=4)
        model = Pipeline([
            ("imputer", SimpleImputer()),
            ("scaler", StandardScaler(with_mean=True, with_std=True)),
            ("lr", LinearRegression())
        ])
        
        model.fit(X_train,y_train)
        # wait it's done?

        # yes
        if self.debug:
            print(f'attrs_regression() complete. Elapsed processing time: {dt.datetime.now() - reg_start}')
        return {
            "model": model,
            "X_train": X_train, "y_train": y_train,
            "X_test": X_test,   "y_test": y_test,
            "features": list(X.columns)
        }
    
    @with_sm_summary
    def interaction_regression(self, category, dependent_variable: str, interaction_variables: list = [], scope='total'): 
        from itertools import combinations
        # initialize df variables
        merged_df, X, y = self._prepare_data(category, dependent_variable, [], scope, self.league)
        # iterate through the provided variables and create new columns for the products
        pairs = list(combinations(interaction_variables,2))
        inter_names = []
        for a, b in pairs:
            inter_name = f'{a}*{b}'
            merged_df[inter_name] = merged_df[a]*merged_df[b]
            inter_names.append(inter_name)
        
        # redefine the independent variables list to include the interactions
        all_features = self._cat_stat_dict(self._attributes_data)[category.capitalize()] + inter_names
        print(all_features)
        X = merged_df[all_features]

        # from here it's the same as before
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=4)
        model = Pipeline([
            ("imputer", SimpleImputer()),
            ("scaler", StandardScaler(with_mean=True, with_std=True)),
            ("lr", LinearRegression())
        ])
        model.fit(X_train,y_train)

        return {
            "model": model,
            "X_train": X_train, "y_train": y_train,
            "X_test": X_test,   "y_test": y_test,
            "features": list(X.columns)
        }

    def attrs_interaction(self, category, dependent_variable: str, independent_variables: list = [], scope='total',degree=2):
        from sklearn.preprocessing import PolynomialFeatures, StandardScaler
        from sklearn.linear_model import ElasticNetCV

        merged_df, X, y = self._prepare_data(category, dependent_variable, independent_variables, scope, self.league)

        if degree > 3:
            degree_warning = input('Interaction function executed with a degree higher than 3. This may require a non-trivial amount of compute to execute.\n\
                    Press Enter to continue or N to stop.')
            if degree_warning.lower() == 'n':
                quit()

        pipe = Pipeline([
            ("poly",   PolynomialFeatures(degree=degree, include_bias=False, interaction_only=True)),
            ("scaler", StandardScaler()),
            ("enet",   ElasticNetCV(l1_ratio=[.2, .5, .8, 1.0], cv=5, max_iter=20000))
        ]).fit(X, y)

        poly = pipe.named_steps["poly"]

        expanded_names = [n.replace(" ", "*") for n in poly.get_feature_names_out(X.columns)]

        coef_series = pd.Series(pipe.named_steps["enet"].coef_, index=expanded_names)
        interactions = coef_series[coef_series.index.str.contains(r"\*")].sort_values(key=abs,ascending=False)

        interactions_df = interactions.reset_index()
        interactions_df.columns = ['Attributes','Values']

        interactions_dict = interactions_df.to_dict()
        interactions_dict = {k:v for k,v in zip(interactions_dict['Attributes'].values(),interactions_dict['Values'].values())}

        return {
            "pipeline": pipe,
            "feature_coefs": coef_series.sort_values(key=abs, ascending=False),
            "interactions":interactions_df,
            "inter_dict":interactions_dict
        }
    
    def attrs_hypotheticals(self,category,dependent_var,independent_vars = [], scope='total'):
        merged_df, dep_var, ind_vars = self._prepare_data(category,dependent_var,independent_vars,scope=scope,league_obj=self.league)
        independent_vars = independent_vars or self._cat_stat_dict(self._attributes_data)[category.capitalize()]
        st_devs = {}
        for ind in independent_vars:
            st_devs[ind] = round(merged_df[ind].std(),2)

        return st_devs
    
    @staticmethod
    def reorder_regression_coefs(res,p_threshold=0.05, descending=True):
        # pass statsmodels regression output as an arg, get tiered sort
        # first segment by significant/insignificant p-value, then order by coef desc
        # significance defined as p < 0.05 by default.

        import numpy as np

        df = pd.DataFrame({
            "coef": res.params,
            "std_err": res.bse,
            "t": res.tvalues,
            "pval_num": res.pvalues,   # keep numeric for sorting
        })

        # 3-tier labeling: significant < marginal < insignificant
        def tier_from_p(p):
            if p < 0.05:
                return "significant"
            elif p < 0.10:
                return "marginal"
            else:
                return "insignificant"

        df["tier"] = df["pval_num"].apply(tier_from_p)
        tier_rank = {"significant": 0, "marginal": 1, "insignificant": 2}
        df["_tier_rank"] = df["tier"].map(tier_rank)

        # sort: tier first, then numeric p-value, then coef
        df = df.sort_values(
            ["_tier_rank", "pval_num", "coef"],
            ascending=[True, True, not descending]
        ).drop(columns="_tier_rank")

        # pretty-print p-values AFTER sorting
        def format_p(p):
            if p < 1e-3:  return "<0.001 ***"
            if p < 1e-2:  return f"{p:.3f} **"
            if p < 0.05:  return f"{p:.3f} *"
            if p < 0.10:  return f"{p:.3f} ·"
            return f"{p:.3f}"

        df["pval"] = df["pval_num"].apply(format_p)
        df = df.drop(columns="pval_num").round({"coef": 6, "std_err": 6, "t": 3})

        return df[["tier", "coef", "std_err", "t", "pval"]]


