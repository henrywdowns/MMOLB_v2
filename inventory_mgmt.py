from utils import Utils

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
        
        if isinstance(stats, dict):
            stats_list = [stats]
        elif isinstance(stats, list):
            stats_list = stats
        else:
            raise TypeError("Unsupported type for stats; expected dict or list of dicts.")

        for stat_block in stats_list:
            for stat in stat_block:
                for cat, val in self.categories.items():
                    if stat in val:
                        agg_dict[cat] += stat_block[stat]

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


if __name__ == '__main__':
    inv = Inventory()
    # updated down through elvis fukuda
    print(inv.get_inventory())
    print(inv.evaluate_stats(inv.inventory['Industrial Slope Ring']))
    print(inv.evaluate_build([v for v in inv.get_inventory().keys()]))