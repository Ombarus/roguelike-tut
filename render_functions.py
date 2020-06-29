import tcod as libtcod
from enum import Enum

class RenderOrder(Enum):
	CORPSE = 1
	ITEM = 2
	ACTOR = 3
	
def get_names_under_mouse(mouse, entities, fov_map):
	(x, y) = (mouse.cx, mouse.cy)
	names = [entity.name for entity in entities
		if entity.x == x and entity.y == y and fov_map.fov[entity.y][entity.x]]
	names = ", ".join(names)
	
	return names.capitalize()
	
def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
	bar_width = int(float(value) / maximum * total_width)
	
	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
	libtcod.console_set_default_background(panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
		
	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, int(x + total_width/2), y, libtcod.BKGND_NONE, 
		libtcod.CENTER, "{}: {}/{}".format(name, value, maximum))

def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, 
	screen_height, bar_width, panel_height, panel_y, mouse, colors):
	if fov_recompute:
		for y in range(game_map.height):
			for x in range(game_map.width):
				visible = fov_map.fov[y][x]
				wall = game_map.tiles[x][y].block_sight
				if visible:
					if wall:
						libtcod.console_set_char_background(con, x, y, colors.get("light_wall"), libtcod.BKGND_SET)
					else:
						libtcod.console_set_char_background(con, x, y, colors.get("light_ground"), libtcod.BKGND_SET)
					game_map.tiles[x][y].explored = True
				elif game_map.tiles[x][y].explored:
					if wall:
						libtcod.console_set_char_background(con, x, y, colors.get("dark_wall"), libtcod.BKGND_SET)
					else:
						libtcod.console_set_char_background(con, x, y, colors.get("dark_ground"), libtcod.BKGND_SET)
	
	entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
	
	for entity in entities_in_render_order:
		if fov_map.fov[entity.y][entity.x]:
			draw_entity(con, entity)
	
	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)
	
	render_bar(panel, 1, 1, bar_width, "HP", player.fighter.hp, player.fighter.max_hp,
		libtcod.light_red, libtcod.darker_red)
		
	libtcod.console_set_default_foreground(panel, libtcod.light_gray)
	libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, 
		get_names_under_mouse(mouse, entities, fov_map))
		
	y = 1
	for message in message_log.messages:
		libtcod.console_set_default_foreground(panel, message.color)
		libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
		y += 1
		
	libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
	libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)
	
def clear_all(con, entities):
	for entity in entities:
		clear_entity(con, entity)
		
def draw_entity(con, entity):
	libtcod.console_set_default_foreground(con, entity.color)
	libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)
	
def clear_entity(con, entity):
	libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)
