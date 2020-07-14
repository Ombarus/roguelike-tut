import tcod as libtcod

from game_states import GameStates

def handle_keys(key, game_state):
	if game_state == GameStates.PLAYERS_TURN:
		return handle_player_turn_keys(key)
	elif game_state == GameStates.PLAYER_DEAD:
		return handle_player_dead_keys(key)
	elif game_state == GameStates.SHOW_INVENTORY or game_state == GameStates.DROP_INVENTORY:
		return handle_inventory_keys(key)
	elif game_state == GameStates.TARGETING:
		return handle_targeting_keys(key)
	elif game_state == GameStates.LEVEL_UP:
		return handle_level_up_menu(key)
	elif game_state == GameStates.CHARACTER_SCREEN:
		return handle_char_screen(key)
	
	return {}
	

def handle_char_screen(key):
	if key.vk == libtcod.KEY_ESCAPE:
		return {"exit":True}
		
	return {}
	
	
def handle_level_up_menu(key):
	if key:
		key_char = chr(key.c)
		
	if key_char == 'a':
		return {"level_up":"hp"}
	if key_char == 'b':
		return {"level_up":"str"}
	if key_char == 'c':
		return {"level_up":"dex"}
		
	return {}
	
	
def handle_main_menu(key):
	key_char = chr(key.c)
	
	if key_char == 'a':
		return {"new_game": True}
	elif key_char == 'b':
		return {"load_game": True}
	elif key_char == 'c' or key.vk == libtcod.KEY_ESCAPE:
		return {"exit":True}
		
	return {}
	
	
def handle_targeting_keys(key):
	if key.vk == libtcod.KEY_ESCAPE:
		return {"exit":True}
		
	return {}
	
def handle_mouse(mouse):
	(x, y) = (mouse.cx, mouse.cy)
	
	if mouse.lbutton_pressed:
		return {"left_click":(x, y)}
	elif mouse.rbutton_pressed:
		return {"right_click":(x, y)}
		
	return {}
	
def handle_inventory_keys(key):
	index = key.c - ord('a')
	
	if index >= 0:
		return {"inventory_index":index}
		
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		return {"fullscreen":True}
	elif key.vk == libtcod.KEY_ESCAPE:
		return {"exit":True}
		
	return {}

def handle_player_dead_keys(key):
	key_char = chr(key.c)
	
	if key_char == 'i':
		return {"show_inventory":True}
		
	if key_char == 'd':
		return {"drop_inventory":True}
		
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		return {"fullscreen":True}
	elif key.vk == libtcod.KEY_ESCAPE:
		return {"exit":True}
	
	return {}
	
def handle_player_turn_keys(key):
	key_char = chr(key.c)
	
	# movement keys
	if key.vk == libtcod.KEY_UP or key_char == 'k' or key.vk == libtcod.KEY_KP8:
		return {"move":(0,-1)}
	elif key.vk == libtcod.KEY_DOWN or key_char == 'j' or key.vk == libtcod.KEY_KP2:
		return {"move":(0,1)}
	elif key.vk == libtcod.KEY_LEFT or key_char == 'h' or key.vk == libtcod.KEY_KP4:
		return {"move":(-1,0)}
	elif key.vk == libtcod.KEY_RIGHT or key_char == 'l' or key.vk == libtcod.KEY_KP6:
		return {"move":(1,0)}
	elif key_char == 'y' or key.vk == libtcod.KEY_KP7:
		return {"move":(-1,-1)}
	elif key_char == 'u' or key.vk == libtcod.KEY_KP9:
		return {"move":(1,-1)}
	elif key_char == 'b' or key.vk == libtcod.KEY_KP1:
		return {"move":(-1,1)}
	elif key_char == 'n' or key.vk == libtcod.KEY_KP3:
		return {"move":(1,1)}
	elif key_char == 'z' or key.vk == libtcod.KEY_KP5:
		return {"wait":True}
		
	if key_char == 'g':
		return {"pickup":True}
		
	if key_char == 'i':
		return {"show_inventory":True}
	if key_char == 'd':
		return {"drop_inventory":True}
		
	if key_char == 'c':
		return {"show_character_screen": True}
		
	if key.vk == libtcod.KEY_ENTER:
		return {'take_stairs':True}
		
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		# Alt+Enter: toggle full screen
		return {"fullscreen": True}
		
	elif key.vk == libtcod.KEY_ESCAPE:
		# Exit the game
		return {"exit": True}
		
	return {}