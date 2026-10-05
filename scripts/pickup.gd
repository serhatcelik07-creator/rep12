extends Area2D
## A trigger tile: coin, spikes, checkpoint or finish flag. Drawn with simple shapes,
## so the game needs no art assets.

signal touched(pickup, player)

enum Kind { COIN, SPIKES, CHECKPOINT, FLAG }

var kind := Kind.COIN
var active := true
var _time := 0.0


func setup(new_kind: Kind, tile: float) -> void:
	kind = new_kind
	var shape := RectangleShape2D.new()
	var offset := Vector2.ZERO
	match kind:
		Kind.COIN:
			shape.size = Vector2(16, 16)
		Kind.SPIKES:
			# Only the pointy lower part hurts.
			shape.size = Vector2(tile - 8.0, tile * 0.45)
			offset = Vector2(0, tile * 0.25)
		Kind.CHECKPOINT, Kind.FLAG:
			shape.size = Vector2(tile * 0.6, tile * 2.0)
			offset = Vector2(0, -tile * 0.5)
	var collision := CollisionShape2D.new()
	collision.shape = shape
	collision.position = offset
	add_child(collision)
	collision_layer = 0
	collision_mask = 2
	body_entered.connect(func(body: Node2D) -> void: touched.emit(self, body))


func _process(delta: float) -> void:
	if kind == Kind.COIN or kind == Kind.FLAG:
		_time += delta
		queue_redraw()


func _draw() -> void:
	match kind:
		Kind.COIN:
			# Fake a spinning coin by squashing it horizontally.
			var squash := absf(cos(_time * 3.0)) * 0.8 + 0.2
			draw_set_transform(Vector2.ZERO, 0.0, Vector2(squash, 1.0))
			draw_circle(Vector2.ZERO, 8.0, Color("#ffcc33"))
			draw_circle(Vector2.ZERO, 5.0, Color("#ffe680"))
			draw_set_transform(Vector2.ZERO)
		Kind.SPIKES:
			for i in 3:
				var x := -16.0 + i * 32.0 / 3.0
				var points := PackedVector2Array([Vector2(x, 16), Vector2(x + 32.0 / 6.0, 0), Vector2(x + 32.0 / 3.0, 16)])
				draw_colored_polygon(points, Color("#d8dde6"))
		Kind.CHECKPOINT:
			var flag_color := Color("#5ad16b") if not active else Color("#7a8299")
			draw_rect(Rect2(-2, -32, 4, 48), Color("#c9c9c9"))
			draw_colored_polygon(PackedVector2Array([Vector2(2, -32), Vector2(20, -25), Vector2(2, -18)]), flag_color)
		Kind.FLAG:
			var wave := sin(_time * 5.0) * 3.0
			draw_rect(Rect2(-2, -48, 4, 64), Color("#e8e8e8"))
			for row in 3:
				for col in 4:
					var c := Color.WHITE if (row + col) % 2 == 0 else Color.BLACK
					draw_rect(Rect2(2 + col * 6, -48 + row * 6 + wave * col / 4.0, 6, 6), c)
