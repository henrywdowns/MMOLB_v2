import polars as pl
import typing
from typing import Optional

class Utils:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def access_json(filename: str) -> dict:
        """
        Checks folder for json of name filename and returns contents as dict.
        If no file matches filename, returns an empty dict.
        """
        import json
        try:
            with open(filename,'r') as f:
                file = json.load(f)
        except FileNotFoundError:
            file = {}
        return file

    @staticmethod
    def write_json(filename: str, data: dict, debug: bool = False) -> None:
        """
        Writes a dict to a json file. As is standard to the json package, if no
        file is found, creates a file. Otherwise overwrites the existing file. 
        """
        import json
        import os
        exists = 'created'
        if os.path.exists(filename):
            exists = 'updated'
        with open(filename,'w') as f:
            json.dump(data,f,indent=4)
        if debug: 
            print(f'File {exists} at {filename}.')
    
    @staticmethod
    def ensure_nested_dict(container: dict, *keys) -> dict:
        """
        Ensure that nested dictionaries exist for each key in *keys* within the given container.
        Returns the innermost nested dict, creating any missing levels along the way.
        
        Example:
            derived = {}
            player_dict = Utils.ensure_nested_dict(derived, team_id, player_id)
            # now derived == {team_id: {player_id: {}}}
            # and player_dict refers to derived[team_id][player_id]
        """
        current = container
        for key in keys:
            # If the key does not exist or isn't a dict, initialize it to an empty dict
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        return current

    @staticmethod
    def printout_header(header_text: str, char: str = '='):
        line_break = ''
        for x in range(int(round(float(len(header_text))/len(char),0))):
            line_break += char
        header_str = f'{line_break}\n{header_text}\n{line_break}'
        return header_str
        
    @staticmethod
    def access_csv(filename: str, to_df: bool = True, debug: bool = False) -> pl.DataFrame:
        """
        Checks folder for csv of name filename and returns contents as dict.
        If no file matches filename, returns an empty dict.
        """
        import csv
        try:
            with open(filename,'r') as f:
                file = csv.DictReader(f)
                if to_df:
                    file = pl.DataFrame(file)
        except FileNotFoundError:
            return {}
        print(f'File {filename} retrieved with data type {type(file)}. Reminder: output is a POLARS df.')
        return file
    
    @staticmethod
    def write_csv(data, filepath: Optional[str] = None, team_name: str = None) -> None: # also accepts polars and pandas dataframes
        """
        Writes a df to a csv file. If no file is found, creates a file. Otherwise overwrites the existing file. 
        """
        import datetime as dt
        import csv

        filename = ''
        if type(data).__name__ == 'DataFrame':
            if 'polars' in str(type(data)):
                if not filepath: filename = team_name.replace(' ','_')
                data = data.to_dicts()
            elif 'pandas' in str(type(data)):
                if not filepath: filename = team_name
                data = data.to_dict(orient="records")
        else:
            filename = data["set"][0]
        if filepath: filename = filepath
        filename+=(f'_export_{dt.datetime.strftime(dt.datetime.now(), '%m%d%y_%H%M')}')
        fieldnames = data[0].keys()
        with open(filename,'w',newline='') as f:
            writer = csv.DictWriter(f,fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f'File {filename} saved successfully.')

    @staticmethod
    def print_all_rows(df: pl.DataFrame) -> None:
        with pl.Config(tbl_rows=-1):
            print(df)
    
    @staticmethod
    def print_all_cols(df: pl.DataFrame) -> None:
        with pl.Config(tbl_cols=-1):
            print(df)

    @staticmethod
    def print_all(df: pl.DataFrame) -> None:
        with pl.Config(tbl_cols=-1,tbl_rows=-1):
            print(df)

    @staticmethod
    def pl_safe_cast(df: pl.DataFrame, col_name: str, data_type: str):
        TYPE_MAP = {
            "int": pl.Int64,
            "float": pl.Float64,
            "str": pl.Utf8,
            "bool": pl.Boolean,
            "date": pl.Date,
            "datetime": pl.Datetime,
            "time": pl.Time,
        }
        try:
            if col_name in df.columns and data_type in TYPE_MAP:
                df = df.with_columns(pl.col(col_name).cast(TYPE_MAP[data_type]))
                return df
            else:
                return df
        except Exception as e:
            print(str(e))
            return df