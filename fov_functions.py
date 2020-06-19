import tcod as libtcod

def initialize_fov(game_map):
	fov_map = libtcod.map_new(game_map.width, game_map.height)
	
	for y in range((game_map.height)):
		for x in range(game_map.width):
			fov_map.transparent[y][x] = not game_map.tiles[x][y].block_sight
			fov_map.walkable[y][x] = not game_map.tiles[x][y].blocked
			
	return fov_map

def recompute_fov(fov_map, x, y, radius, light_walls, algorithm=0):
	fov_map.compute_fov(x, y, radius, light_walls, algorithm)