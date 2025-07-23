from utils import Utils
import pandas as pd
import pprint

"""
Mostly meant as an evaluation tool before purchasing items, and to figure out which positions
are most suited for which items.
"""
class Inventory:
    def __init__(self):
        # set up categories to be a set of stat categories, and a list of general stats
        self.inventory = Utils.write_or_access_json('inventory.json')
        self.categories = {}
        value_dicts = list(Utils.access_json('player_attributes.json').values())
        for val_dict in value_dicts:
            for category, inner_dict in val_dict.items():
                if not isinstance(inner_dict, dict):
                    continue
                if category not in self.categories:
                    self.categories[category] = set()
                self.categories[category].update(inner_dict.keys())
        for category in self.categories:
            self.categories[category] = sorted(list(self.categories[category]))

    def evaluate_stats(self, stats: dict | list[dict]) -> dict:
        agg_dict = {category: 0 for category in self.categories}

        stats_list = stats if isinstance(stats, list) else [stats]

        for stat_block in stats_list:
            for raw_key, value in stat_block.items():
                normalized = raw_key.capitalize()
                for cat, val_list in self.categories.items():
                    if normalized in val_list:
                        agg_dict[cat] += value

        return agg_dict

    def add_inventory(self, name: str, stats: dict, eval: bool = True, dupe: bool = False) -> dict:
        existing = self.inventory.get(name)
        if not existing:
            self.inventory[name] = stats
            print(f'Added {name} to inventory.')
        else:
            existing_list = (
                [existing] if isinstance(existing, dict) else existing
            )
            if stats in existing_list and not dupe:
                print(f'{name} with identical stats already exists. Use dupe=True to force add.')
                return self.inventory
            if isinstance(existing, dict):
                self.inventory[name] = [existing, stats]
            else:
                self.inventory[name].append(stats)
            print(f'Added another version of {name} to inventory.')
        if eval:
            self.evaluate_stats(stats)
        return self.inventory


    def bulk_add(self,inv_list:list) -> dict:
        for item in list:
            self.add_inventory(item)
        return self.inventory
    
    def get_inventory(self, name=None):
        if name:
            return self.inventory[name]
        else:
            return self.inventory
    
    def del_inventory(self, name: str) -> None:
        del self.inventory[name]
    
    def save_inventory(self) -> None:
        Utils.write_json('inventory.json',self.inventory)
        print('Inventory saved.')

    def evaluate_build(self,names:list = []):
        agg_dict = {category: 0 for category in self.categories}
        if names:
            for item in names:
                eval_item = self.evaluate_stats(self.inventory[item])
                for cat in agg_dict.keys():
                    agg_dict[cat] += eval_item[cat]
        return agg_dict
    
    def inventory_map(self) -> pd.DataFrame:
        # want to display players, possibly stats, to show who has what - the API does not support this at all right now to my knowledge.
        # also want to display each item on a grid (y = item, x = stat) and whether it's equipped or not (player name as value). also not supported lol
        rows = []
        for item_name, stats in inv.inventory.items():
            if isinstance(stats, list):
                for stat_dict in stats:
                    row = {'item': item_name}
                    row.update(stat_dict)
                    rows.append(row)
            else:
                row = {'item': item_name}
                row.update(stats)
                rows.append(row)
        df = pd.DataFrame(rows)
        df = df.sort_values('item').reset_index(drop=True)
        return df
    
    def find_stats(self,stats: list) -> pd.DataFrame:
        map = self.inventory_map()
        cap_stats = [stat.capitalize() for stat in stats]
        item_stats = ['item'] + cap_stats
        print(type(map))
        df = map[item_stats]
        df = df.dropna(subset=cap_stats,how='all')
        return df.sort_values(by=cap_stats[0],ascending=False).reset_index(drop=True)
    
    def build_player_inv_catalogue(self):
        import requests
        chicken_id = '680e477a7d5b06095ef46ad1'
        base_url = 'https://mmolb.com/api/'
        r = requests.get(f'{base_url}/team/{chicken_id}').json()
        player_ids = [player['PlayerID'] for player in r['Players']]
        player_base = f'{base_url}/player/'
        player_objs = [requests.get(f'{player_base}{p_id}').json() for p_id in player_ids]
        player_equips = [player['Equipment'] for player in player_objs]
        pprint.pprint(player_equips[0])

        # framework for saving/writing an item in human-readable way
        full_inv = {}
        for equip in player_equips:
            for slot, details in equip.items():
                item_name = (' '.join(details.get('Prefixes', [])+[details['Name']]+details.get('Suffixes', []))).strip()
                bonus = {effect['Attribute']: round(effect['Value']*100,0) for effect in details['Effects']}
                if full_inv.get(item_name,''):
                    full_inv[item_name] = [full_inv[item_name]] + [bonus]
                else:
                    full_inv[item_name] = bonus
        pprint.pprint(full_inv)
    
    def build_player_inv_catalogue_gpt(self):
        import requests, pprint

        chicken_id   = '680e477a7d5b06095ef46ad1'
        base_url     = 'https://mmolb.com/api'
        # fetch team → list of player IDs
        team_data    = requests.get(f'{base_url}/team/{chicken_id}').json()
        player_ids   = [p['PlayerID'] for p in team_data['Players']]

        # fetch each player’s full object
        player_base  = f'{base_url}/player/'
        player_objs  = [requests.get(f'{player_base}{pid}').json() for pid in player_ids]

        catalogue = []
        for player in player_objs:
            owner = f"{player['FirstName']} {player['LastName']}"
            equip = player.get('Equipment', {})

            # for each slot (Accessory, Body, Feet, etc.)
            for slot, details in equip.items():
                prefixes = details.get('Prefixes', [])
                name     = details.get('Name', '')
                suffixes = details.get('Suffixes', [])

                item_name = ' '.join(prefixes + [name] + suffixes)

                catalogue.append({
                    'Owner':   owner,
                    'Slot':    slot,
                    'ItemName': item_name
                })

        # pretty-print, or return for further processing
        pprint.pprint(catalogue)
        return catalogue


        

if __name__ == '__main__':
    inv = Inventory()
    # updated down through elvis fukuda
    # print(inv.get_inventory())
    # print(inv.evaluate_stats(inv.inventory['Industrial Slope Ring']))
    # print(inv.evaluate_build([v for v in inv.get_inventory().keys()]))
    # print(inv.find_stats(['contact']))
    inv.build_player_inv_catalogue_gpt()