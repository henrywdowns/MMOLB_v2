# stupid little script i had chatgpt finish for me bc i was lazy and burnt out
import json
from typing import Optional
import polars as pl
from utils import Utils

class ScoutReport:
    def __init__(self):
        self.scouting_report = Utils.access_json('chicken_scout_reports.json')

    def scouting_report(self):
        adjective_ratings = {
            "barely": 1,
            "not": 2,
            "decent": 3,
            "quite":4,
            "very": 5,
            "extremely": 6
        }

        parsed_dict = {}
        keywords = {}
        keywords_scored = {}

        for player, report in self.scouting_report.items():
            # 1) split into sentences and strip out empties
            sentences = [s.strip() for s in report.replace('\n\n', ' ').split('.') if s.strip()]
            parsed_dict[player] = sentences

            # 2) initialize per-player mappings
            keywords[player] = {}
            keywords_scored[player] = {}

            # 3) skip the first two sentences and scan for adjectives
            for sentence in sentences[2:]:
                words = sentence.split()
                for i, word in enumerate(words):
                    if word in adjective_ratings:
                        # determine which following word to grab
                        if word == "decent":
                            # "decent" modifies the word two over
                            if i + 2 < len(words):
                                target = words[i + 2]
                            else:
                                continue
                        else:
                            # other adjectives modify the very next word
                            if i + 1 < len(words):
                                target = words[i + 1]
                            else:
                                continue

                        keywords[player][target] = word
                        keywords_scored[player][target] = adjective_ratings[word]
        return keywords, keywords_scored


    @staticmethod
    def scout_rep_df(player_names: Optional[list] = None,transpose: bool = False, truncate: bool = False) -> pl.DataFrame:
        parsed_dict = {}
        scout_dict = Utils.access_json('chicken_scout_reports.json')
        if not truncate:
            pl.Config.set_fmt_str_lengths(1000)
        for player, report in scout_dict.items():
            # 1) split into sentences and strip out empties
            sentences = [s.strip() for s in report.replace('\n\n', ' ').split('.') if s.strip()]
            if 'pitching' in sentences[3].split():
                sentences[3], sentences[4], sentences[7], sentences[8] = (
                sentences[7], sentences[8], sentences[3], sentences[4]
                )                    

            parsed_dict[player] = sentences
        df = pl.DataFrame(parsed_dict)
        df = df.transpose(include_header=True,header_name="Player",column_names=["Overall","Batting_Order","Luck","Batting_Topline","Batting_Details",\
                                                                                "Defensive_Topline","Defensive_Details","Pitching_Topline","Pitching_Details",\
                                                                                "Baserunning_Topline","Baserunning_Details"])
        if player_names: df = df.filter(pl.col("Player").is_in(player_names))
        if transpose: 
            column_names = player_names if player_names else df.select("Player").to_series().to_list()
            df = df.transpose(include_header=True, header_name="Stat", column_names=column_names)
        return df
    
    @staticmethod
    def keyword_search(keyword: str) -> tuple[pl.DataFrame,list[str]]:
        report = ScoutReport.scout_rep_df()

        matches = []

        for row in report.iter_rows(named=True):
            player = row["Player"]
            for col, val in row.items():
                if col == "Player":
                    continue
                if val is not None and keyword in str(val):
                    matches.append({
                        "Player": player,
                        "Stat": col,
                        "Text": val
                    })
        player_list = pl.DataFrame(matches).select("Player").unique().to_series().to_list()
        return pl.DataFrame(matches), player_list

if __name__ == '__main__':
    #print(json.dumps(scouting_report()[0],indent=4), json.dumps(scouting_report()[1],indent=4))
    scout = ScoutReport()
    # Utils.print_all(ScoutReport.scout_rep_df(transpose=True))
    Utils.print_all(ScoutReport.keyword_search('arm'))
    
