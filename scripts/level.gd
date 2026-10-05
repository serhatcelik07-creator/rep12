extends Node2D
## Builds a playable level from an ASCII map (see levels.gd for the legend).

signal coin_collected(player)
signal flag_reached(player)

const Pickup := preload("res://scripts/pickup.gd")
const TILE := 32.0
const GROUND_COLOR := Color("#4a7a3a")
const DIRT_COLOR := Color("#6b4a2f")
const PLATFORM_COLOR := Color("#a87a4a")

var spawn_points: Array[Vector2] = []
var bounds := Rect2()
var coin_total := 0

var _solids: Array[Rect2] = []
var _platforms: Array[Rect2] = []
var _grid: Array = []


func build(map: Array) -> void:
	_grid = map
	var width := 0
	for y in map.size():
		var row: String = map[y]
		width = maxi(width, row.length())
		var x := 0
		while x < row.length():
			var c := row[x]
			if c == "#" or c == "=":
				# Merge horizontal runs into one collider.
				var start := x
				while x < row.length() and row[x] == c:
					x += 1
				_add_block(start, y, x - start, c == "=")
				continue
			var center := Vector2((x + 0.5) * TILE, (y + 0.5) * TILE)
			match c:
				"C":
					_add_pickup(Pickup.Kind.COIN, center)
					coin_total += 1
				"^":
					_add_pickup(Pickup.Kind.SPIKES, center)
				"K":
					_add_pickup(Pickup.Kind.CHECKPOINT, center)
				"F":
					_add_pickup(Pickup.Kind.FLAG, center)
				"S":
					spawn_points.append(center)
			x += 1
	bounds = Rect2(0, 0, width * TILE, map.size() * TILE)
	if spawn_points.is_empty():
		spawn_points.append(Vector2(TILE * 2, TILE * 2))
	queue_redraw()


func _add_block(tile_x: int, tile_y: int, length: int, one_way: bool) -> void:
	var rect := Rect2(tile_x * TILE, tile_y * TILE, length * TILE, TILE)
	if one_way:
		rect.size.y = 10.0
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	var shape := RectangleShape2D.new()
	shape.size = rect.size
	var collision := CollisionShape2D.new()
	collision.shape = shape
	collision.position = rect.get_center()
	collision.one_way_collision = one_way
	body.add_child(collision)
	add_child(body)
	if one_way:
		_platforms.append(rect)
	else:
		_solids.append(rect)


func _add_pickup(kind: Pickup.Kind, center: Vector2) -> void:
	var pickup := Pickup.new()
	pickup.position = center
	pickup.setup(kind, TILE)
	pickup.touched.connect(_on_pickup_touched)
	add_child(pickup)


func _on_pickup_touched(pickup: Pickup, player: Node2D) -> void:
	if not player.has_method("die"):
		return
	match pickup.kind:
		Pickup.Kind.COIN:
			if pickup.active:
				pickup.active = false
				pickup.queue_free()
				player.coins += 1
				coin_collected.emit(player)
		Pickup.Kind.SPIKES:
			player.call_deferred("die")
		Pickup.Kind.CHECKPOINT:
			pickup.active = false
			pickup.queue_redraw()
			player.respawn_point = pickup.position
		Pickup.Kind.FLAG:
			flag_reached.emit(player)


func _draw() -> void:
	for rect in _solids:
		draw_rect(rect, DIRT_COLOR)
		# Grass only on tiles that have open air above them.
		var tile_y := int(rect.position.y / TILE)
		for i in int(rect.size.x / TILE):
			var tile_x := int(rect.position.x / TILE) + i
			if tile_y == 0 or _tile_at(tile_x, tile_y - 1) != "#":
				draw_rect(Rect2(rect.position.x + i * TILE, rect.position.y, TILE, 8), GROUND_COLOR)
	for rect in _platforms:
		draw_rect(rect, PLATFORM_COLOR)
		draw_rect(rect, PLATFORM_COLOR.darkened(0.4), false, 2.0)


func _tile_at(x: int, y: int) -> String:
	if y < 0 or y >= _grid.size():
		return "."
	var row: String = _grid[y]
	return row[x] if x >= 0 and x < row.length() else "."
