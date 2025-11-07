
import requests
from utils import Utils

chicken_id = '680e477a7d5b06095ef46ad1'
base_url = 'https://mmolb.com/api/'
base_game = f'{base_url}/game/'

r = requests.get(f'{base_url}/team/{chicken_id}')

def make_cal():
    seasons = {}
    for season_num, id in enumerate(r.json()['SeasonRecords'].keys()):
        days_dict = {}
        # should spit out a dict where key "Days" has list of day IDs as value
        season = requests.get(f'{base_url}/season/{id}').json()
        # list of day ids in season
        days = season['Days']
        # produce day number and ID, for a sub-dict. iterate and 
        for day_num, id in enumerate(days):
            days_dict[day_num + 1] = id
        seasons[season_num] = [id,days_dict]            

    return seasons

calendar = make_cal()

Utils.write_json('calendar.json',calendar)

s2d220 = calendar[2][1][120]
s2d221 = calendar[2][1][121]
print(s2d221)

def get_day(day,team=None):
    day_data = requests.get(f'{base_url}/day/{day}').json()
    if team:
        team_game = {}
        for game in day_data['Games']:
            if game['AwayTeamID'] == team or game['HomeTeamID'] == team:
                day_data['Games'] = game
    return day_data

print(Utils.printout_header('S2 D120'))
print(get_day(s2d220,chicken_id))

game = requests.get(f'{base_url}/game/685f84e43f9d4b6ccc602eb6')
print(game.json()['Stats'][chicken_id]['6841af60e63d9bb87288a02b'])

class TimeSeries:
    def __init__(self, team_id):
        self.team_id = team_id
        self.calendar = self.make_cal()
        print(self.team_id)
    
    def make_cal(self,league='lesser'):
        seasons = {}
        for season_num, id in enumerate(r.json()['SeasonRecords'].keys()):
            days_dict = {}
            # should spit out a dict where key "Days" has list of day IDs as value
            season = requests.get(f'{base_url}/season/{id}').json()
            # list of day ids in season
            days = season['Days']
            # produce day number and ID, for a sub-dict. iterate and 
            for day_num, id in enumerate(days):
                if (league.lower() == 'lesser' and (day_num + 1)%2 == 0) or (league.lower() == 'greater' and (day_num +1)%2 == 1) or league.lower() not in ['greater','lesser']:
                    days_dict[day_num + 1] = id
            seasons[season_num] = [id,days_dict]            

        return seasons        

    def get_day(self,day,season = None):
        if not season:
            season = len(self.calendar) - 1
        if str(day).isnumeric():
            print('numeric')
            day_id = self.calendar[season][1][day]
        else:
            day_id = day
        print(f'Season {season} Day {day}')
        day_data = requests.get(f'{base_url}/day/{day_id}').json()
        x = 0
        for game in day_data['Games']:
            x += 1
            if game['AwayTeamID'] == self.team_id or game['HomeTeamID'] == self.team_id:
                day_data['Games'] = game
                break
        else:
            print('No matching ID')
            day_data = None
        return day_data

    def build_game_history(self, start = 0, season = None):
        game_id_list = []
        if not season:
            season = len(self.calendar) - 1
        print(len(self.calendar))
        for x in range(start,len(self.calendar[season][1]),2):
            try:
                game_id = self.get_day(x)['Games']['GameID']
                game_id_list.append(game_id)
            except:
                break
                


    """
    TODO: GAME_HISTORY_HANDLER needs to check for json and if none, create
    then find/create team ID as key, and scan game_history. wherever the most recent
    day is, take note of that day, then get_day() starting from then until get_day() returns None
    """
    

    def handle_game_history(self, league = 'lesser'):
        # attempt to access a game history file, then attempt to access data for team_id.
        game_history = {}
        game_id_list = []
        try:
            game_history_json = Utils.access_json('game_history.json')
            if game_history_json.get(self.team_id):
                game_history = game_history_json.get(self.team_id)

        except:
            Utils.write_json('game_history.json',{self.team_id: game_history})

        last_game = len(game_history) * 2
        if league == 'greater':
            last_game -= 1
        
        safety = 0
        while True:
            safety += 1
            if safety > 400:
                break
            for day in self.make_cal():
                if day%2 == 0:
                    game_id_list.append(self.get_day(day))

                    '''for game_id in game_id_list:
            x = 0
            x +=1
            game_log = requests.json(f'{base_game}/{game_id}')
            if x < 3:
                print(game_log)'''



    
if __name__ == '__main__':
    chicken_day = TimeSeries(chicken_id)
    test_day = chicken_day.get_day(52,season=2)
    print(Utils.printout_header(f'Day {test_day['Day']}'))
    print(test_day)
    print(test_day['Games'])

    #chicken_day.handle_game_history()