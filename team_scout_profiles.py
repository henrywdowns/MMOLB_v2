from utils import Utils
import spicy_chicken_stats as scs

chicken_id = '680e477a7d5b06095ef46ad1'
chicken = scs.Team(chicken_id)

def make_json():
    chicken_scout_dict = {}

    chk_names = chicken.player_names
    for player_name in chk_names:
        for position, options in Utils.access_json('player_draft_attributes.json').items():
            for option in options:
                if option['Name'] == player_name:
                    chicken_scout_dict[player_name] = option['ScoutingReport']


    Utils.write_json('chicken_scout_reports.json',chicken_scout_dict)

def check_dupes():
    names = {}
    for position, options in Utils.access_json('player_draft_attributes.json').items():
        for option in options:
            if option['Name'] in names.keys():
                names[option['Name']] += 1
            else:
                names[option['Name']] = 1
    return names

if __name__ == '__main__':
    names = check_dupes()
    for name, count in names.items():
        if count > 1:
            print(name, count)
