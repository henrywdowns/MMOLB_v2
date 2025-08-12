from utils import Utils
import pandas as pd
import pprint
import requests
import typing

"""
Pull items to create live catalog of inventory, both loose and equipped
"""
class Inventory:
    def __init__(self, team_id = '680e477a7d5b06095ef46ad1'):
        self.base_url = 'https://mmolb.com/api'
        self.team_id = team_id
        self.inventory = Utils.write_or_access_json('inventory_v2.json') #cache
        self.categories = {} # attr categories
        self.players = {} # hold player objects bc why not
        value_dicts = list(Utils.access_json('player_attributes.json').values()) # list of player attrs and attr cats
        for val_dict in value_dicts: # loop through value dicts and set up self.cats as one of each cat and component attr
            for category, inner_dict in val_dict.items():
                if not isinstance(inner_dict, dict):
                    continue
                if category not in self.categories:
                    self.categories[category] = set()
                self.categories[category].update(inner_dict.keys())
        for category in self.categories:
            self.categories[category] = sorted(list(self.categories[category]))
        self.team_data = Utils.write_or_access_json('inv_team_data.json',data = requests.get(f'{self.base_url}/team/{self.team_id}').json())
    
    def update_player_inv_catalogue(self, save:bool = False) -> dict:
        # fetch team → list of player IDs
        player_ids = [p['PlayerID'] for p in self.team_data['Players']]

        # fetch each player’s full object
        player_base = f'{self.base_url}/player/'
        player_objs = [requests.get(f'{player_base}{pid}').json() for pid in player_ids]

        catalogue = []
        for player in player_objs:
            owner = f'{player['FirstName']} {player['LastName']}'
            equip = player.get('Equipment', {})
            # for each slot (Accessory, Body, Feet, etc.)
            for slot, details in equip.items():
                if details:
                    prefixes = details.get('Prefixes', [])
                    name = details.get('Name', '')
                    suffixes = details.get('Suffixes', [])
                    effects = details.get('Effects')
                    bonuses = {effect['Attribute']: effect['Value'] for effect in effects}
                    item_name = ' '.join(prefixes + [name] + suffixes)

                catalogue.append({
                    item_name: {
                        'Owner': owner,
                        'Slot': slot,
                        'Bonus': bonuses
                    }
                })
        # repeat the process - only slightly differently, for the unequipped inv
        # currently not exposed publicly so i just copied it out of the network inspector response
        unequipped = Utils.access_json('inventory_hardcode.json')['inventory']

        for details in unequipped:
            prefixes = details.get('Prefixes',[])
            name = details.get('Name', '')
            slot = details.get('Slot','')
            suffixes = details.get('Suffixes', [])
            effects = details.get('Effects')
            bonuses = {effect['Attribute']: effect['Value'] for effect in effects}
            item_name = ' '.join(prefixes + [name] + suffixes)
                
            catalogue.append({
                item_name: {
                    'Owner': None,
                    'Slot': slot,
                    'Bonus': bonuses
                }
            })
        if save:
            Utils.write_json('inventory_v2.json',catalogue)
        return catalogue
    
    def get_items_by_attribute(self, attribute: str, unequipped=True) -> list:
        result = []
        for item in self.inventory:
            if attribute.capitalize() in list(item.values())[0].get('Bonus'):
                if list(item.values())[0].get('Owner') and unequipped:
                    continue
                result.append(item)
        sorted_result = sorted(result, key = lambda x: list(x.values())[0].get('Bonus')[attribute.capitalize()],reverse=True)
        return sorted_result
    
    def get_players_by_attribute(self, attribute: str, ascending: bool = True) -> dict:
        result = {attribute.capitalize():[]}
        attr_db = Utils.access_json('attributes_db.json')
        players = attr_db.get(self.team_id,[])
        category = None
        matched_attr = None
        for cat, attrs in self.categories.items():
            for a in attrs:
                if a.lower() == attribute.lower():
                    category = cat
                    matched_attr = a
                    break
            if category:
                break
        if not category:
            print(f'Attribute {attribute} not found in categories')
            return []

        for player_wrapper in players:
            player_id, attr_data = list(player_wrapper.items())[0]
            attr_block = attr_data.get(category, {})

            if matched_attr in attr_block:
                attr_value = attr_block[matched_attr]
            
                for team_player in self.team_data['Players']:
                    if team_player['PlayerID'] == player_id:
                        pname = f'{team_player['FirstName']} {team_player['LastName']}'
                        result[attribute.capitalize()].append({pname: attr_value})

        result[attribute.capitalize()] = sorted(result[attribute.capitalize()], key = lambda x: list(x.values())[0], reverse=(not ascending))
        return result
    
    def add_item_bonuses(self, item_names: typing.List[str]) -> dict:
        result = {}
        for item_name in item_names:
            item_obj = None
            for item in self.inventory:
                if item_name in item:
                    item_obj = item[item_name]
                    break
            if not item_obj:
                print(f'[WARN] didnt find the name {item_name}')
            for attr in item_obj['Bonus'].keys():
                if result.get(attr):
                    result[attr] += item_obj['Bonus'][attr]
                else:
                    result[attr] = item_obj['Bonus'][attr]
        for key, value in result.items():
            result[key] = round(value,2)
        return result
    
    def detailed_add_item_bonuses(self, item_names: typing.List[str]) -> dict:
        # Raw structure: attr → {slot → value}
        attr_slot_map = {}

        for item_name in item_names:
            item_obj = None
            slot = None

            for item in self.inventory:
                if item_name in item:
                    item_obj = item[item_name]
                    slot = item_obj.get('Slot', 'Unknown')
                    break

            if not item_obj:
                print(f'[WARN] Didn’t find item with name: {item_name}')
                continue

            for attr, val in item_obj['Bonus'].items():
                if attr not in attr_slot_map:
                    attr_slot_map[attr] = {}
                attr_slot_map[attr][slot] = attr_slot_map[attr].get(slot, 0) + val

        # Now flatten into your requested string format
        summary = {}
        for attr, slot_contribs in attr_slot_map.items():
            total = round(sum(slot_contribs.values()), 2)
            parts = [f"{round(val, 2)} {slot}" for slot, val in slot_contribs.items()]
            breakdown = '; '.join(parts)
            summary[attr] = f"{total} -- {breakdown}"

        return summary

    def player_summary(self,player_name: str):
        player_id = None
        player_inv = []
        for player in self.team_data['Players']:
            if player_name.lower() == f'{player['FirstName']} {player['LastName']}'.lower():
                player_id = player['PlayerID']
                break
        player_attrs = None
        for attr_dict in Utils.access_json('attributes_db.json')[self.team_id]:
            if list(attr_dict.keys())[0] == player_id:
                player_attrs = attr_dict[player_id]
        #player_data = requests.get(f'{self.base_url}/player/{player_id}')
        for item in self.inventory:
            if list(item.values())[0]['Owner']:
                if list(item.values())[0]['Owner'].lower() == player_name.lower():
                    player_inv.append(item)
        inv_names = [list(itemobj.keys())[0] for itemobj in player_inv]
        player_bonuses = self.detailed_add_item_bonuses(inv_names)

        return {player_name.capitalize(): {
            'Player Attributes': player_attrs,
            'Player Item Bonuses': player_bonuses,
            #'Player Inventory': player_inv
        }}


if __name__ == '__main__':
    inv = Inventory()
    inv.update_player_inv_catalogue(save=True)
    pprint.pprint(inv.player_summary('amanda huylroyce'))
    pprint.pprint(inv.player_summary('jacob decker'))