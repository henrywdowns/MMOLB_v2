from box import Box
from MMOLB import APIHandler
from pprint import pprint

handler = APIHandler()
chk = handler.get_team()
chk_lite = handler.get_league(populate='Spicy Chicken Crunchwraps').get_team('Spicy Chicken Crunchwraps')

pprint.pprint(chk_lite.players)