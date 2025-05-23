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
    def write_json(filename: str, data: dict) -> None:
        """
        Writes a dict to a json file. As is standard to the json package, if no
        file is found, creates a file. Otherwise overwrites the existing file. 
        """
        import json
        import sys
        exists = 'created'
        if sys.os.exists(filename):
            exists = 'updated'
        with open(filename,'w') as f:
            json.dump(data,filename,indent=4)
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
