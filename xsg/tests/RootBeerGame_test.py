import game  # just copy the game.py and station.py modules here and remove the xsg reference from import stations statement in game.py
import json

with open('RootBeerGame.json', 'r') as game_file:
    game_data = json.load(game_file)

G = game.Game(config=game_data)
G.Run()
print(G.Debug_Report())
G.Plots()
