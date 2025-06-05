from utils import Utils
import requests

scout_profile = Utils.access_json('player_draft_attributes.json')

r = requests.get('https://mmolb.com/team/680e477a7d5b06095ef46ad1')

print(r.text)