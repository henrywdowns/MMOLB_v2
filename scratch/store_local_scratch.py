"""
this could be simpler and more functional.
how it works now: takes team object, validates and applies timestamps, saves file.

can/should use Utils.access_json and Utils.write_json
"""
from utils import Utils

def store_local(self,team_object: object = None, get_team_id: bool = None) -> None:
        import datetime as dt
        import json
        filename = 'teams.json'

        def set_local_data_attribute() -> None:
            temp_local_data = ltd.TeamStorage()
            self.team_stored_data = temp_local_data.get_team_data(self.id)
            print(f'Stored data: {self.team_stored_data.keys()}')

        # get_team_id allows for pulling out of local - a little janky, i know
        if get_team_id: # get_team_id should be a literal id
            try:
                return Utils.access[get_team_id]
            except Exception as e:
                print(f'Error: {str(e)}')
                return
        # if get_team_id is None and there's also no team object to speak of, our business is done here
        if not team_object:
            print('No team data found.')
            return
        # otherwise, we locate the file...
        try:
            with open(filename,'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f'No file found: {str(e)}')
            data = {}
        # ...and dump the new json
        data[self.id] = {}
        data[self.id]['timestamp'] = dt.datetime.now()
        with open(filename,'w') as f:
            data[team_object.id] = team_object.team_data
            json.dump(data, f, indent=4)
            print(f'{filename} successfully saved.')  
            #set_local_data_attribute()