import sys
import os
os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"]
import glob

import tcod as libtcod
from input_handlers import handle_keys
from entity import Entity
from render_functions import clear_all, render_all
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates

DATA_FOLDER = "data"
FONT_FILE = os.path.join(DATA_FOLDER, "arial10x10.png")

def main():
	screen_width = 80
	screen_height = 50
	map_width = 80
	map_height = 45
	room_max_size = 10
	room_min_size = 6
	max_rooms = 30
	max_monsters_per_room = 3
	
	fov_algorithm = 0
	fov_light_walls = True
	fov_radius = 10
	
	colors = {
		"dark_wall": libtcod.Color(0, 0, 100),
		"dark_ground": libtcod.Color(50, 50, 150),
		"light_wall": libtcod.Color(130, 110, 50),
		"light_ground": libtcod.Color(200, 180, 50)
	}
	
	fov_recompute = True
	game_map = GameMap(map_width, map_height)
	player = Entity(0, 0, '@', libtcod.white, "Player", blocks=True)
	entities = [player]
	game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)
	
	libtcod.console_set_custom_font(FONT_FILE, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_init_root(screen_width, screen_height, "ombarus libtcod tutorial revised", False)
	con = libtcod.console_new(screen_width, screen_height)
	
	key = libtcod.Key()
	mouse = libtcod.Mouse()
	
	fov_map = initialize_fov(game_map)
	game_state = GameStates.PLAYERS_TURN
	
	while not libtcod.console_is_window_closed():
		if fov_recompute:
			recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)
			
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
		render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors)
		libtcod.console_flush()
		
		clear_all(con, entities)
		fov_recompute = False
		
		action = handle_keys(key)
		
		move = action.get("move")
		exit = action.get("exit")
		fullscreen = action.get("fullscreen")
		
		if move and game_state == GameStates.PLAYERS_TURN:
			dx, dy = move
			if not game_map.is_blocked(player.x + dx, player.y + dy):
				destination_x = player.x + dx
				destination_y = player.y + dy
				target = player.get_blocking_entities_at_location(entities, destination_x, destination_y)
				if target:
					print("You kick the {} in the shins, much to its annoyance!".format(target.name))
				else:
					fov_recompute = True
					player.move(dx, dy)
					
			game_state = GameStates.ENEMY_TURN
			
		if exit:
			return True
			
		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
			
		if game_state == GameStates.ENEMY_TURN:
			for entity in entities:
				if entity != player and fov_map.fov[entity.y][entity.x]:
					print("The {} ponders the meaning of its existance.".format(entity.name))
					
			game_state = GameStates.PLAYERS_TURN
	
if __name__ == "__main__":
	main()