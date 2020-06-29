class BasicMonster:
	def take_turn(self, target, fov_map, game_map, entities):
		monster = self.owner
		results = []
		if fov_map.fov[monster.y][monster.x]:
			dist = monster.distance_to(target)
			if monster.distance_to(target) >= 2:
				monster.move_astar(target, entities, game_map)
				
			elif target.fighter.hp > 0:
				attack_results = monster.fighter.attack(target)
				results.extend(attack_results)
				
		return results