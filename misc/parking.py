import requests
import polars as pl


url = 'https://data.cityofnewyork.us/resource/nc67-uf89.json'


r = requests.get(url)

df = pl.DataFrame(r.json())

print(df.head())