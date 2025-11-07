import pandas as pd

class MMOLBStats:
    def __init__(self,team_data,api_handler) -> None:
        self.team_data = team_data
        self.league_id = getattr(team_data, 'league', None)
        self.handler = api_handler
        self.team_hitting = self.handler.fc_team_stats(stats_type='hitting')
        self.team_pitching = self.handler.fc_team_stats(stats_type='pitching')
        self.league_hitting = self.handler.fc_league_stats(stats_type='hitting')
        self.league_pitching = self.handler.fc_league_stats(stats_type='pitching')

# ---------- helpers ----------
    @staticmethod
    def _safe_div(n, d):
        # robust to Series/scalar denominators and zeros
        if isinstance(d, pd.Series):
            d2 = d.replace(0, pd.NA)
            return n / d2
        else:
            if d == 0:
                if isinstance(n, pd.Series):
                    return pd.Series(pd.NA, index=n.index, dtype="float")
                return pd.NA
            return n / d

    def _get(self, scope: str, kind: str) -> pd.DataFrame:
        match kind:
            case "hitting" | "batting": # hitting
                return self.team_hitting.copy() if scope == "team" else self.league_hitting.copy()
            case "pitching":  # pitching
                return self.team_pitching.copy() if scope == "team" else self.league_pitching.copy()
        raise ValueError("kind must be 'hitting' or 'pitching'")

    # ---------- base derived ----------
    def basic_hitting(self, scope: str) -> pd.DataFrame:
        df = self._get(scope, "hitting")
        df["hitting"]  = df.eval("singles + doubles + triples + home_runs")
        df["TB"] = df.eval("singles + 2*doubles + 3*triples + 4*home_runs")

        df["BA"]  = self._safe_div(df["hitting"], df["at_bats"])
        df["OBP"] = self._safe_div(
            df["hitting"] + df["walked"] + df["hit_by_pitch"],
            df["at_bats"] + df["walked"] + df["hit_by_pitch"] + df["sac_flies"]
        )
        df["SLG"] = self._safe_div(df["TB"], df["at_bats"])
        df["OPS"] = df["OBP"] + df["SLG"]

        df["BABIP"] = self._safe_div(
            df["hitting"] - df["home_runs"],
            df["at_bats"] - df["struck_out"] - df["home_runs"] + df["sac_flies"]
        )

        df["SB%"] = self._safe_div(df["stolen_bases"], df["stolen_bases"] + df["caught_stealing"])
        df["K%"]  = self._safe_div(df["struck_out"], df["plate_appearances"])
        df["BB%"] = self._safe_div(df["walked"], df["plate_appearances"])
        df["ISO"] = df["SLG"] - df["BA"]
        return df

    def basic_pitching(self, scope: str) -> pd.DataFrame:
        df = self._get(scope, "pitching")
        df["IP"]   = self._safe_div(df["outs"], 3)
        df["ERA"]  = self._safe_div(df["earned_runs"] * 9, df["IP"])
        df["WHIP"] = self._safe_div(df["walks"] + df["hits_allowed"], df["IP"])

        df["K9"]  = self._safe_div(df["strikeouts"] * 9, df["IP"])
        df["BB9"] = self._safe_div(df["walks"] * 9, df["IP"])
        df["HR9"] = self._safe_div(df["home_runs_allowed"] * 9, df["IP"])

        c = self.league_fip_constant()  # computed safely (no recursion)
        df["FIP"] = self._safe_div(
            13*df["home_runs_allowed"] + 3*(df["walks"] + df["hit_batters"]) - 2*df["strikeouts"],
            df["IP"]
        ) + c
        return df

    # ---------- league-derived constant (no recursion) ----------
    def league_fip_constant(self) -> float:
        """
        c = lg_ERA - ((13*lgHR + 3*(lgBB+lgHBP) - 2*lgK) / lgIP)
        Computed directly from raw league pitching + IP, avoiding calls to basic_pitching().
        """
        lg = self.league_pitching.copy()
        lg["IP"] = self._safe_div(lg["outs"], 3)

        lgIP  = lg["IP"].sum(min_count=1)
        lgER  = lg["earned_runs"].sum(min_count=1)
        lgHR  = lg["home_runs_allowed"].sum(min_count=1)
        lgBB  = lg["walks"].sum(min_count=1)
        lgHBP = lg["hit_batters"].sum(min_count=1)
        lgK   = lg["strikeouts"].sum(min_count=1)

        if pd.isna(lgIP) or lgIP == 0:
            return 0.0

        lgERA    = (lgER * 9) / lgIP
        fip_core = (13*lgHR + 3*(lgBB + lgHBP) - 2*lgK) / lgIP
        if pd.isna(lgERA) or pd.isna(fip_core):
            return 0.0
        return float(lgERA - fip_core)

    # ---------- league-based plus/minus ----------
    def batting_plus(self, scope: str) -> pd.DataFrame:
        df = self.basic_hitting(scope)
        lg = self.basic_hitting("league")

        for stat in ["OBP", "SLG", "OPS", "BA", "BABIP", "ISO"]:
            if stat in df and stat in lg:
                mu = lg[stat].mean(skipna=True)
                if pd.notna(mu) and mu != 0:
                    df[f"{stat}+"] = 100 * self._safe_div(df[stat], mu)
                else:
                    df[f"{stat}+"] = pd.NA
        return df

    def pitching_minus(self, scope: str) -> pd.DataFrame:
        df = self.basic_pitching(scope)
        lg = self.basic_pitching("league")

        for stat in ["ERA", "FIP", "WHIP"]:
            if stat in df and stat in lg:
                mu = lg[stat].mean(skipna=True)
                if pd.notna(mu) and mu != 0:
                    df[f"{stat}-"] = 100 * self._safe_div(df[stat], mu)  # lower is better
                else:
                    df[f"{stat}-"] = pd.NA
        return df

    # ---------- optional: percentiles & z-scores ----------
    def add_percentiles(self, scope: str, cols: list[str]) -> pd.DataFrame:
        hit_cols = {"BA","OBP","SLG","OPS","BABIP","ISO","SB%","K%","BB%"}
        df = self.basic_hitting(scope) if set(cols) & hit_cols else self.basic_pitching(scope)
        for c in cols:
            if c in df:
                asc = c in ["ERA", "FIP", "WHIP"]  # smaller better
                df[f"{c}_pct"] = df[c].rank(pct=True, ascending=asc)
        return df

    def add_zscores(self, scope: str, cols: list[str]) -> pd.DataFrame:
        hit_cols = {"BA","OBP","SLG","OPS","BABIP","ISO","SB%","K%","BB%"}
        df = self.basic_hitting(scope) if set(cols) & hit_cols else self.basic_pitching(scope)
        lg = self.basic_hitting("league") if set(cols) & hit_cols else self.basic_pitching("league")
        for c in cols:
            if c in df and c in lg:
                mu, sd = lg[c].mean(skipna=True), lg[c].std(skipna=True)
                df[f"{c}_z"] = (df[c] - mu) / sd if pd.notna(sd) and sd else pd.NA
        return df

    # ---------- master: cohesive, rounded outputs ----------
    def _id_cols(self, df: pd.DataFrame) -> list[str]:
        # adjust this list to match your schema
        candidates = ["player", "player_name", "name", "player_id", "id", "team", "team_name"]
        return [c for c in candidates if c in df.columns]

    def master_summary(self, rounding: int = 2) -> dict:
        th = self.basic_hitting("team")
        lh = self.basic_hitting("league")
        tp = self.basic_pitching("team")
        lp = self.basic_pitching("league")

        hitting  = pd.concat({"team": th, "league": lh})
        print(hitting)
        pitching = pd.concat({"team": tp, "league": lp})

        hp_cols = ["BA+","OBP+","SLG+","OPS+","BABIP+","ISO+"]
        pm_cols = ["ERA-","FIP-","WHIP-"]

        bp_team = self.batting_plus("team")
        pm_team = self.pitching_minus("team")

        idh = self._id_cols(bp_team)
        idp = self._id_cols(pm_team)

        h_plus  = bp_team[idh + [c for c in hp_cols if c in bp_team.columns]] if not bp_team.empty else pd.DataFrame()
        p_minus = pm_team[idp + [c for c in pm_cols if c in pm_team.columns]] if not pm_team.empty else pd.DataFrame()

        # if both have the same id column(s), align on them; otherwise just concat side-by-side
        if not h_plus.empty and not p_minus.empty:
            # try to merge on common id columns
            common_ids = [c for c in idh if c in idp]
            if common_ids:
                team_plus_minus = h_plus.merge(p_minus, on=common_ids, how="outer")
            else:
                team_plus_minus = pd.concat([h_plus, p_minus], axis=1)
        else:
            team_plus_minus = pd.concat([h_plus, p_minus], axis=1)

        league_means = pd.DataFrame({
            "BA":   [lh["BA"].mean(skipna=True)],
            "OBP":  [lh["OBP"].mean(skipna=True)],
            "SLG":  [lh["SLG"].mean(skipna=True)],
            "OPS":  [lh["OPS"].mean(skipna=True)],
            "ERA":  [lp["ERA"].mean(skipna=True)],
            "FIP":  [lp["FIP"].mean(skipna=True)],
            "WHIP": [lp["WHIP"].mean(skipna=True)],
        })

        for df in (hitting, pitching, team_plus_minus, league_means):
            num = df.select_dtypes(include="number").columns
            df[num] = df[num].round(rounding)

        return {
            "hitting": hitting,
            "pitching": pitching,
            "team_plus_minus": team_plus_minus,
            "league_means": league_means,
        }