extends CharacterBody2D
## A player character. Each player reads its own keyboard scheme and/or gamepad,
## so several players can share one screen (local multiplayer).

signal died(player)

enum Keys { NONE, WASD, ARROWS, BOTH }

const SIZE := Vector2(24, 30)
const SPEED := 260.0
const GROUND_ACCEL := 2200.0
const GROUND_FRICTION := 2600.0
const AIR_ACCEL := 1400.0
const GRAVITY := 1500.0
const JUMP_VELOCITY := -560.0
const MAX_FALL_SPEED := 900.0
const COYOTE_TIME := 0.1
const JUMP_BUFFER_TIME := 0.12
const STICK_DEADZONE := 0.25

var index := 0
var color := Color.WHITE
var show_tag := false
var joy_device := -1
var keys := Keys.NONE
var respawn_point := Vector2.ZERO
var coins := 0
var deaths := 0
var controls_enabled := true

var _coyote := 0.0
var _jump_buffer := 0.0
# Starts true so the button press that started the game doesn't trigger a jump.
var _jump_was_down := true
var _facing := 1.0


func _ready() -> void:
	var shape := RectangleShape2D.new()
	shape.size = SIZE
	var collision := CollisionShape2D.new()
	collision.shape = shape
	add_child(collision)
	collision_layer = 2
	# Collide with the world and with other players, so players can stand on each other.
	collision_mask = 1 | 2


func _physics_process(delta: float) -> void:
	var direction := _read_axis() if controls_enabled else 0.0
	var jump_down := _read_jump() if controls_enabled else false
	var jump_pressed := jump_down and not _jump_was_down
	_jump_was_down = jump_down

	if is_on_floor():
		_coyote = COYOTE_TIME
	else:
		_coyote -= delta
	if jump_pressed:
		_jump_buffer = JUMP_BUFFER_TIME
	else:
		_jump_buffer -= delta

	velocity.y = minf(velocity.y + GRAVITY * delta, MAX_FALL_SPEED)
	if _jump_buffer > 0.0 and _coyote > 0.0:
		velocity.y = JUMP_VELOCITY
		_jump_buffer = 0.0
		_coyote = 0.0
	elif velocity.y < 0.0 and not jump_down:
		# Releasing jump early cuts the jump short.
		velocity.y += GRAVITY * 1.5 * delta

	var accel := GROUND_ACCEL if is_on_floor() else AIR_ACCEL
	if direction == 0.0 and is_on_floor():
		accel = GROUND_FRICTION
	velocity.x = move_toward(velocity.x, direction * SPEED, accel * delta)
	if direction != 0.0:
		_facing = signf(direction)

	move_and_slide()
	queue_redraw()


func die() -> void:
	deaths += 1
	respawn()
	died.emit(self)


func respawn() -> void:
	position = respawn_point
	velocity = Vector2.ZERO


func _read_axis() -> float:
	var axis := 0.0
	if keys == Keys.WASD or keys == Keys.BOTH:
		axis += float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A))
	if keys == Keys.ARROWS or keys == Keys.BOTH:
		axis += float(Input.is_physical_key_pressed(KEY_RIGHT)) - float(Input.is_physical_key_pressed(KEY_LEFT))
	if joy_device >= 0:
		var stick := Input.get_joy_axis(joy_device, JOY_AXIS_LEFT_X)
		if absf(stick) > STICK_DEADZONE:
			axis += stick
		axis += float(Input.is_joy_button_pressed(joy_device, JOY_BUTTON_DPAD_RIGHT))
		axis -= float(Input.is_joy_button_pressed(joy_device, JOY_BUTTON_DPAD_LEFT))
	return clampf(axis, -1.0, 1.0)


func _read_jump() -> bool:
	if keys == Keys.WASD or keys == Keys.BOTH:
		if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_SPACE):
			return true
	if keys == Keys.ARROWS or keys == Keys.BOTH:
		if Input.is_physical_key_pressed(KEY_UP):
			return true
	if joy_device >= 0 and Input.is_joy_button_pressed(joy_device, JOY_BUTTON_A):
		return true
	return false


func _draw() -> void:
	var body := Rect2(-SIZE / 2.0, SIZE)
	draw_rect(body, color)
	draw_rect(body, color.darkened(0.45), false, 2.0)
	# Eyes look in the walking direction.
	for eye_x in [-3.0, 5.0]:
		var eye := Vector2(eye_x + 2.0 * _facing - 2.0, -9.0)
		draw_rect(Rect2(eye, Vector2(4, 7)), Color.WHITE)
		draw_rect(Rect2(eye + Vector2(1.0 + _facing, 2), Vector2(2, 4)), Color.BLACK)
	if show_tag:
		var font := ThemeDB.fallback_font
		var tag := "P%d" % (index + 1)
		draw_string(font, Vector2(-10, -SIZE.y / 2.0 - 6.0), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, color.lightened(0.3))
