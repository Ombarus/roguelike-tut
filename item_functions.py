import tcod as libtcod

from game_messages import Message
from components.ai import ConfusedMonster

def heal(*args, **kwargs):
	entity = args[0]
	amount = kwargs.get("amount")
	
	results = []
	
	if entity.fighter.hp == entity.fighter.max_hp:
		results.append({"consumed":False, "message":Message("You are already at full health", libtcod.yellow)})
	else:
		entity.fighter.heal(amount)
		results.append({"consumed":True, "message":Message("Your wounds start to feel better!", libtcod.green)})
		
	return results
	
def cast_lightning(*args, **kwargs):
	caster = args[0]
	entities = kwargs.get("entities")
	fov_map = kwargs.get("fov_map")
	damage = kwargs.get("damage")
	maximum_range = kwargs.get("maximum_range")
	
	results = []
	
	target = None
	closest_distance = maximum_range + 1
	
	for entity in entities:
		if entity.fighter and entity != caster and fov_map.fov[entity.y, entity.x]:
			distance = caster.distance_to(entity)
			
			if distance < closest_distance:
				target = entity
				closest_distance = distance
				
	if target:
		results.append({"consumed":True, "target":target, 
			"message":Message("A lightning bolt strikes the {} with a loud thunder! The damage is {}".format(
				target.name, damage), libtcod.red)})
		results.extend(target.fighter.take_damage(damage))
	else:
		results.append({"consumed":False, "target":None, 
			"message":Message("No enemy is close enough to strike.", libtcod.red)})
		
	return results
			
def cast_fireball(*args, **kwargs):
	entities = kwargs.get("entities")
	fov_map = kwargs.get("fov_map")
	damage = kwargs.get("damage")
	radius = kwargs.get("radius")
	target_x = kwargs.get("target_x")
	target_y = kwargs.get("target_y")
	
	results = []
	
	if not fov_map.fov[target_y, target_x]:
		results.append({"consumed":False, "message":Message(
			"You cannot target a tile outside your field of view.", libtcod.yellow)})
		return results
		
	results.append({"consumed":True, "message":Message(
		"The fireball explodes, burning everything within {} tiles!".format(radius), libtcod.orange)})
		
	for entity in entities:
		if entity.distance(target_x, target_y) <= radius and entity.fighter:
			results.append({"message":Message(
				"The {} gets burned for {} hit points.".format(entity.name, damage),
				libtcod.orange)})
			results.extend(entity.fighter.take_damage(damage))
			
	return results
			
			
def cast_confuse(*args, **kwargs):
	entities = kwargs.get("entities")
	fov_map = kwargs.get("fov_map")
	target_x = kwargs.get("target_x")
	target_y = kwargs.get("target_y")
	
	results = []
	
	if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
		results.append({"consumed":False, 
			"message":Message("You cannot target a tile outside your field of view.", libtcod.yellow)})
		return results
		
	for entity in entities:
		if entity.x == target_x and entity.y == target_y and entity.ai:
			confused_ai = ConfusedMonster(entity.ai, 10)
			
			confused_ai.owner = entity
			entity.ai = confused_ai
			
			results.append({"consumed":True, 
				"message":Message("The eyes of the {} look vacant, as he starts to stumble around!".format(
					entity.name), libtcod.light_green)})
			break
	else:
		results.append({"consumed":False, 
			"message":Message("There is no targetable enemy at that location", libtcod.yellow)})
			
	return results
		
			
			
			
			
			
			
			
			
			
			