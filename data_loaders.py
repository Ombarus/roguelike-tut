import shelve
import os
import pickle

SAVE_FILE = "savegame.dat"


def save_game(player, entities, game_map, message_log, game_state):
	data_file = {}
	data_file["player_index"] = entities.index(player)
	data_file["entities"] = entities
	data_file["game_map"] = game_map
	data_file["message_log"] = message_log
	data_file["game_state"] = game_state
	
	pickle.dump(data_file, open(SAVE_FILE, "wb"))
		
		
def load_game():
	if not os.path.isfile(SAVE_FILE):
		raise FileNotFoundError
		
	data_file = pickle.load(open(SAVE_FILE, "rb"))
	
	player_index = data_file["player_index"]
	entities = data_file["entities"]
	game_map = data_file["game_map"]
	message_log = data_file["message_log"]
	game_state = data_file["game_state"]
	
	player = entities[player_index]
	
	return player, entities, game_map, message_log, game_state