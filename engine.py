import sys
import os
os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"]
import glob

import tcod as libtcod
from input_handlers import handle_keys
from entity import Entity
from render_functions import clear_all, render_all, RenderOrder
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from game_messages import MessageLog

DATA_FOLDER = "data"
FONT_FILE = os.path.join(DATA_FOLDER, "arial10x10.png")

def main():
	screen_width = 80
	screen_height = 50
	map_width = 80
	map_height = 43
	room_max_size = 10
	room_min_size = 6
	max_rooms = 30
	max_monsters_per_room = 3
	
	fov_algorithm = 0
	fov_light_walls = True
	fov_radius = 10
	
	bar_width = 20
	panel_height = 7
	panel_y = screen_height - panel_height
	
	message_x = bar_width + 2
	message_width = screen_width - bar_width - 2
	message_height = panel_height - 1
	
	colors = {
		"dark_wall": libtcod.Color(0, 0, 100),
		"dark_ground": libtcod.Color(50, 50, 150),
		"light_wall": libtcod.Color(130, 110, 50),
		"light_ground": libtcod.Color(200, 180, 50)
	}
	
	fov_recompute = True
	game_map = GameMap(map_width, map_height)
	fighter_component = Fighter(hp=30, defense=2, power=5)
	player = Entity(0, 0, '@', libtcod.white, "Player", blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component)
	entities = [player]
	game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)
	
	libtcod.console_set_custom_font(FONT_FILE, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_init_root(screen_width, screen_height, "ombarus libtcod tutorial revised", False)
	con = libtcod.console_new(screen_width, screen_height)
	panel = libtcod.console_new(screen_width, panel_height)
	
	key = libtcod.Key()
	mouse = libtcod.Mouse()
	
	fov_map = initialize_fov(game_map)
	message_log = MessageLog(message_x, message_width, message_height)
	game_state = GameStates.PLAYERS_TURN
	
	while not libtcod.console_is_window_closed():
		if fov_recompute:
			recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)
			
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
		render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, 
			screen_height, bar_width, panel_height, panel_y, mouse, colors)
		libtcod.console_flush()
		
		clear_all(con, entities)
		fov_recompute = False
		
		action = handle_keys(key)
		
		move = action.get("move")
		exit = action.get("exit")
		fullscreen = action.get("fullscreen")
		
		player_turn_results = []
		
		if move and game_state == GameStates.PLAYERS_TURN:
			dx, dy = move
			if not game_map.is_blocked(player.x + dx, player.y + dy):
				destination_x = player.x + dx
				destination_y = player.y + dy
				target = player.get_blocking_entities_at_location(entities, destination_x, destination_y)
				if target:
					attack_results = player.fighter.attack(target)
					player_turn_results.extend(attack_results)
				else:
					fov_recompute = True
					player.move(dx, dy)
					
			game_state = GameStates.ENEMY_TURN
			
		if exit:
			return True
			
		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
			
		for player_turn_result in player_turn_results:
			message = player_turn_result.get("message")
			dead_entity = player_turn_result.get("dead")
			if message:
				message_log.add_message(message)
			if dead_entity:
				if dead_entity == player:
					message, game_state = kill_player(dead_entity)
				else:
					message = kill_monster(dead_entity)
				
				message_log.add_message(message)
				
		if game_state == GameStates.ENEMY_TURN:
			for entity in entities:
				if entity.ai:
					enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)
					
					for enemy_turn_result in enemy_turn_results:
						message = enemy_turn_result.get("message")
						dead_entity = enemy_turn_result.get("dead")
						
						if message:
							message_log.add_message(message)
						if dead_entity:
							if dead_entity == player:
								message, game_state = kill_player(dead_entity)
							else:
								message = kill_monster(dead_entity)
								
							message_log.add_message(message)
							
						if game_state == GameStates.PLAYER_DEAD:
							break
					
					if game_state == GameStates.PLAYER_DEAD:
						break
			else:
				game_state = GameStates.PLAYERS_TURN
	
if __name__ == "__main__":
	main()