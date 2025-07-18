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

    def evaluate_stats(self, stats: dict) -> dict:
        agg_dict = {category: 0 for category in self.categories}
        for stat in stats.keys():
            for cat, val in self.categories.items():
                if stat in val:
                    agg_dict[cat] += stats[stat]
        return agg_dict

    def add_inventory(self, name: str, stats: dict, eval: bool = True, dupe: bool = False) -> dict:
        if not self.inventory.get(name):
            self.inventory[name] = stats
        else:
            if self.inventory[name] == stats and dupe == False:
                print(f'Name and value for {name} already exist in dict. Use dupe=True to add anyway.')
                return self.inventory
            if isinstance(self.inventory, str):
                temp = self.inventory[name]
                self.inventory[name] = [temp]
            self.inventory[name].append(stats)
        print(f'Added {name} to inventory.')
        if eval:
            self.evaluate_stats(stats)
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
    # down through rick somersbyshire
    print(inv.evaluate_build([v for v in inv.get_inventory().keys()]))
    