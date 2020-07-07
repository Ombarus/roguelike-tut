import sys
import os
os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"]
import glob

import tcod as libtcod
from input_handlers import handle_keys, handle_mouse
from entity import Entity
from render_functions import clear_all, render_all, RenderOrder
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from game_messages import MessageLog, Message
from components.inventory import Inventory

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
	max_items_per_room = 2
	
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
	inventory_component = Inventory(26)
	player = Entity(0, 0, '@', libtcod.white, "Player", blocks=True, render_order=RenderOrder.ACTOR, 
		fighter=fighter_component, inventory=inventory_component)
	entities = [player]
	game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, 
		player, entities, max_monsters_per_room, max_items_per_room)
	
	libtcod.console_set_custom_font(FONT_FILE, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_init_root(screen_width, screen_height, "ombarus libtcod tutorial revised", False)
	con = libtcod.console_new(screen_width, screen_height)
	panel = libtcod.console_new(screen_width, panel_height)
	
	key = libtcod.Key()
	mouse = libtcod.Mouse()
	
	fov_map = initialize_fov(game_map)
	message_log = MessageLog(message_x, message_width, message_height)
	game_state = GameStates.PLAYERS_TURN
	previous_game_state = game_state
	targeting_item = None
	
	while not libtcod.console_is_window_closed():
		if fov_recompute:
			recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)
			
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
		render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, 
			screen_height, bar_width, panel_height, panel_y, mouse, colors, game_state)
		libtcod.console_flush()
		
		clear_all(con, entities)
		fov_recompute = False
		
		action = handle_keys(key, game_state)
		mouse_action = handle_mouse(mouse)
		
		move = action.get("move")
		pickup = action.get("pickup")
		show_inventory = action.get("show_inventory")
		drop_inventory = action.get("drop_inventory")
		inventory_index = action.get("inventory_index")
		exit = action.get("exit")
		fullscreen = action.get("fullscreen")
		
		left_click = mouse_action.get("left_click")
		right_click = mouse_action.get("right_click")
		
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
			
		if pickup and game_state == GameStates.PLAYERS_TURN:
			for entity in entities:
				if entity.item and entity.x == player.x and entity.y == player.y:
					pickup_results = player.inventory.add_item(entity)
					player_turn_results.extend(pickup_results)
					break
			else:
				message_log.add_message(Message("Tehre is nothing here to pick up.", libtcod.yellow))
				
		if show_inventory:
			previous_game_state = game_state
			game_state = GameStates.SHOW_INVENTORY
			
		if drop_inventory:
			previous_game_state = game_state
			game_state = GameStates.DROP_INVENTORY
			
		if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
			item = player.inventory.items[inventory_index]
			if game_state == GameStates.SHOW_INVENTORY:
				player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
			elif game_state == GameStates.DROP_INVENTORY:
				player_turn_results.extend(player.inventory.drop_item(item))
			
		if game_state == GameStates.TARGETING:
			if left_click:
				target_x, target_y = left_click
				
				item_use_results = player.inventory.use(
					targeting_item, 
					entities=entities,
					fov_map=fov_map,
					target_x=target_x, target_y=target_y)
					
				player_turn_results.extend(item_use_results)
			elif right_click:
				player_turn_results.append({"targeting_cancelled":True})
			
			
		if exit:
			if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
				game_state = previous_game_state
			elif game_state == GameStates.TARGETING:
				player_turn_results.append({"targeting_cancelled":True})
			else:
				return True
			
		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
			
		for player_turn_result in player_turn_results:
			message = player_turn_result.get("message")
			dead_entity = player_turn_result.get("dead")
			item_added = player_turn_result.get("item_added")
			item_consumed = player_turn_result.get("consumed")
			item_dropped = player_turn_result.get("item_dropped")
			targeting = player_turn_result.get("targeting")
			targeting_cancelled = player_turn_result.get("targeting_cancelled")
			
			if message:
				message_log.add_message(message)
			if dead_entity:
				if dead_entity == player:
					message, game_state = kill_player(dead_entity)
				else:
					message = kill_monster(dead_entity)
				
				message_log.add_message(message)
			if item_added:
				entities.remove(item_added)
				game_state = GameStates.ENEMY_TURN
			if item_consumed:
				game_state = GameStates.ENEMY_TURN
			if item_dropped:
				entities.append(item_dropped)
				game_state = GameStates.ENEMY_TURN
			if targeting:
				previous_game_state = GameStates.PLAYERS_TURN
				game_state = GameStates.TARGETING
				targeting_item = targeting
				message_log.add_message(targeting_item.item.targeting_message)
			if targeting_cancelled:
				game_state = previous_game_state
				message_log.add_message(Message("Targeting cancelled"))
			
				
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