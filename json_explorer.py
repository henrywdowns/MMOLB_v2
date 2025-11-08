from box import Box
from MMOLB import APIHandler
import pprint

handler = APIHandler()
chk = handler.get_team()
chk_lite = handler.get_league(populate='Spicy Chicken Crunchwraps').get_team('Spicy Chicken Crunchwraps')

# print('=================================================================')
pprint.pprint(chk_lite.players[0])
# print('*****************************************************************')
# pprint.pprint(chk.players[0].attributes)