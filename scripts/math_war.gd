extends Control
## Matematik Savaşı: 2-4 players answer the same math question on one shared screen.
## The four choices sit on the four directions (up, right, down, left).
## The first correct answer hits every other player for one heart. A wrong answer
## costs your own heart and locks you out until the next question.
## The last player with hearts left wins.
## Players can also throw emojis from their equipped pack at their rival.

signal finished(winner: int, hearts: Array)
signal taunted(from: int, to: int, emoji: String)

const EmojiPacks := preload("res://scripts/emoji_packs.gd")

enum Phase { ASKING, REVEAL, OVER }

const START_HEARTS := 5
const QUESTION_TIME := 10.0
const MIN_QUESTION_TIME := 5.0
const REVEAL_TIME := 1.8
const MAX_QUESTIONS := 30
const STICK_THRESHOLD := 0.6
# Keyboard answer keys per player, in direction order: up, right, down, left.
const KEYMAPS := [
	[KEY_W, KEY_D, KEY_S, KEY_A],
	[KEY_UP, KEY_RIGHT, KEY_DOWN, KEY_LEFT],
	[KEY_I, KEY_L, KEY_K, KEY_J],
	[KEY_KP_8, KEY_KP_6, KEY_KP_5, KEY_KP_4],
]
const KEY_HINTS := ["W A S D", "Ok tuşları", "I J K L", "Num 8 4 5 6"]
const PAD_BUTTONS := [JOY_BUTTON_DPAD_UP, JOY_BUTTON_DPAD_RIGHT, JOY_BUTTON_DPAD_DOWN, JOY_BUTTON_DPAD_LEFT]
const CHOICE_OFFSETS: Array[Vector2] = [Vector2(0, -150), Vector2(330, 0), Vector2(0, 150), Vector2(-330, 0)]
const CHOICE_SIZE := Vector2(200, 80)
# Emoji taunt keys per player, one per pack slot.
const TAUNT_KEYS := [
	[KEY_Q, KEY_E, KEY_R],
	[KEY_COMMA, KEY_PERIOD, KEY_SLASH],
	[KEY_U, KEY_O, KEY_Y],
	[KEY_KP_7, KEY_KP_9, KEY_KP_1],
]
const TAUNT_HINTS := [["Q", "E", "R"], [",", ".", "/"], ["U", "O", "Y"], ["N7", "N9", "N1"]]
const TAUNT_PAD_BUTTONS := [JOY_BUTTON_X, JOY_BUTTON_Y, JOY_BUTTON_B]
const TAUNT_COOLDOWN := 2.0
const TAUNT_TIME := 1.6
# Share of TAUNT_TIME spent flying; the rest is the hit animation on the rival.
const TAUNT_FLIGHT_SHARE := 0.7

var player_count := 2
var colors: Array[Color] = []
var hearts: Array[int] = []
var question := {}
var question_number := 0
var time_left := 0.0
var phase := Phase.ASKING
# Direction each player picked for the current question, -1 = not yet.
var picks: Array[int] = []
# Player who answered the current question correctly first, -1 = nobody.
var hitter := -1
var rng := RandomNumberGenerator.new()
# Equipped emojis per player (EmojiPacks.TAUNT_SLOTS each).
var loadouts: Array = []
# Thrown emojis: {from, to, emoji, t} with t going 0 -> 1 (flight, then a pop on the rival).
var taunts: Array = []

var _pads: Array[int] = []
# Joypad device -> last left stick direction (-1 = centered), so a held stick answers once.
var _stick_dir := {}
var _reveal_left := 0.0
var _taunt_cooldown: Array[float] = []
# Seconds since start, drives idle animations.
var _anim_time := 0.0


## `emoji_packs` holds the equipped pack id per player; missing entries use the free pack.
func setup(count: int, player_colors: Array[Color], seed_value: int = 0, emoji_packs: Array = []) -> void:
	player_count = count
	colors = player_colors
	hearts.clear()
	loadouts.clear()
	_taunt_cooldown.clear()
	taunts.clear()
	for i in count:
		hearts.append(START_HEARTS)
		var pack_id: String = emoji_packs[i] if i < emoji_packs.size() else EmojiPacks.FREE_PACK
		loadouts.append(EmojiPacks.loadout(pack_id))
		_taunt_cooldown.append(0.0)
	if seed_value != 0:
		rng.seed = seed_value
	else:
		rng.randomize()
	_pads = Input.get_connected_joypads()
	question_number = 0
	_next_question()


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


# --- Questions --------------------------------------------------------------

## Builds a question that gets harder with `level` (0 = first question).
## Returns {text, answer, choices (4 ints), correct (index of the answer in choices)}.
static func make_question(level: int, gen: RandomNumberGenerator) -> Dictionary:
	var ops := ["+", "-"]
	if level >= 3:
		ops.append("×")
	if level >= 6:
		ops.append("÷")
	var op: String = ops[gen.randi_range(0, ops.size() - 1)]
	var top := mini(10 + level * 5, 100)
	var table := mini(5 + level, 12)
	var a := 0
	var b := 0
	var result := 0
	match op:
		"+":
			a = gen.randi_range(1, top)
			b = gen.randi_range(1, top)
			result = a + b
		"-":
			a = gen.randi_range(1, top)
			b = gen.randi_range(0, a)
			result = a - b
		"×":
			a = gen.randi_range(2, table)
			b = gen.randi_range(2, table)
			result = a * b
		"÷":
			b = gen.randi_range(2, table)
			result = gen.randi_range(2, table)
			a = b * result

	var choices: Array[int] = [result]
	var spread := maxi(3, int(result / 5.0))
	while choices.size() < 4:
		var wrong := result + gen.randi_range(-spread, spread)
		if wrong >= 0 and not choices.has(wrong):
			choices.append(wrong)
	for i in range(choices.size() - 1, 0, -1):
		var j := gen.randi_range(0, i)
		var tmp := choices[i]
		choices[i] = choices[j]
		choices[j] = tmp
	return {"text": "%d %s %d" % [a, op, b], "answer": result, "choices": choices, "correct": choices.find(result)}


func question_time() -> float:
	return maxf(MIN_QUESTION_TIME, QUESTION_TIME - (question_number - 1) * 0.25)


func _next_question() -> void:
	question_number += 1
	question = make_question(question_number - 1, rng)
	picks.clear()
	for i in player_count:
		picks.append(-1)
	hitter = -1
	time_left = question_time()
	phase = Phase.ASKING
	queue_redraw()


# --- Answers ----------------------------------------------------------------

## Player `player` picks the choice in direction `dir` (0 up, 1 right, 2 down, 3 left).
func answer(player: int, dir: int) -> void:
	if phase != Phase.ASKING or player < 0 or player >= player_count:
		return
	if hearts[player] <= 0 or picks[player] != -1:
		return
	picks[player] = dir
	if dir == question["correct"]:
		hitter = player
		for i in player_count:
			if i != player and hearts[i] > 0:
				hearts[i] -= 1
		_reveal()
	else:
		hearts[player] -= 1
		if alive_count() <= 1 or _waiting_count() == 0:
			_reveal()
	queue_redraw()


func alive_count() -> int:
	var n := 0
	for h in hearts:
		if h > 0:
			n += 1
	return n


func _waiting_count() -> int:
	var n := 0
	for i in player_count:
		if hearts[i] > 0 and picks[i] == -1:
			n += 1
	return n


## Player `player` throws the emoji in `slot` at their rival. Returns false while on cooldown.
func taunt(player: int, slot: int) -> bool:
	if phase == Phase.OVER or player < 0 or player >= player_count:
		return false
	if slot < 0 or slot >= EmojiPacks.TAUNT_SLOTS or _taunt_cooldown[player] > 0.0:
		return false
	var target := taunt_target(player)
	var emoji: String = loadouts[player][slot]
	taunts.append({"from": player, "to": target, "emoji": emoji, "t": 0.0})
	_taunt_cooldown[player] = TAUNT_COOLDOWN
	taunted.emit(player, target, emoji)
	queue_redraw()
	return true


## The rival a player's emojis fly at: the other player with the most hearts.
func taunt_target(player: int) -> int:
	var target := -1
	for i in player_count:
		if i != player and (target == -1 or hearts[i] > hearts[target]):
			target = i
	return target


func _reveal() -> void:
	phase = Phase.REVEAL
	_reveal_left = REVEAL_TIME


func _finish() -> void:
	phase = Phase.OVER
	# Most hearts wins; a tie (or everyone out) is a draw (-1).
	var winner := -1
	var best := -1
	for i in player_count:
		if hearts[i] > best:
			best = hearts[i]
			winner = i
		elif hearts[i] == best:
			winner = -1
	if best <= 0:
		winner = -1
	finished.emit(winner, hearts.duplicate())


func _process(delta: float) -> void:
	for i in player_count:
		_taunt_cooldown[i] = maxf(0.0, _taunt_cooldown[i] - delta)
	_anim_time += delta
	for t in taunts:
		t["t"] += delta / TAUNT_TIME
	taunts = taunts.filter(func(t: Dictionary) -> bool: return t["t"] < 1.0)
	match phase:
		Phase.ASKING:
			time_left -= delta
			if time_left <= 0.0:
				time_left = 0.0
				_reveal()
		Phase.REVEAL:
			_reveal_left -= delta
			if _reveal_left <= 0.0:
				if alive_count() <= 1 or question_number >= MAX_QUESTIONS:
					_finish()
				else:
					_next_question()
	queue_redraw()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		for p in player_count:
			var dir: int = KEYMAPS[p].find(event.physical_keycode)
			if dir != -1:
				answer(p, dir)
			var slot: int = TAUNT_KEYS[p].find(event.physical_keycode)
			if slot != -1:
				taunt(p, slot)
	elif event is InputEventJoypadButton and event.pressed:
		var dir: int = PAD_BUTTONS.find(event.button_index)
		if dir != -1:
			answer(_pads.find(event.device), dir)
		var slot: int = TAUNT_PAD_BUTTONS.find(event.button_index)
		if slot != -1:
			taunt(_pads.find(event.device), slot)
	elif event is InputEventJoypadMotion:
		if event.axis == JOY_AXIS_LEFT_X or event.axis == JOY_AXIS_LEFT_Y:
			_on_stick(event.device)


func _on_stick(device: int) -> void:
	var stick := Vector2(Input.get_joy_axis(device, JOY_AXIS_LEFT_X), Input.get_joy_axis(device, JOY_AXIS_LEFT_Y))
	var dir := -1
	if stick.length() > STICK_THRESHOLD:
		if absf(stick.x) > absf(stick.y):
			dir = 1 if stick.x > 0.0 else 3
		else:
			dir = 2 if stick.y > 0.0 else 0
	if dir != _stick_dir.get(device, -1) and dir != -1:
		answer(_pads.find(device), dir)
	_stick_dir[device] = dir


# --- Drawing ----------------------------------------------------------------

func _draw() -> void:
	if question.is_empty():
		return
	var font := get_theme_default_font()
	var w := size.x
	var h := size.y
	var dim := Color("#9aa3c0")
	var gold := Color("#ffcc33")

	draw_string(font, Vector2(0, 48), "MATEMATİK SAVAŞI  •  Soru %d" % question_number,
			HORIZONTAL_ALIGNMENT_CENTER, w, 24, dim)
	var bar := Rect2(w * 0.25, 64, w * 0.5, 12)
	draw_rect(bar, Color(1, 1, 1, 0.15))
	var frac := clampf(time_left / question_time(), 0.0, 1.0)
	draw_rect(Rect2(bar.position, Vector2(bar.size.x * frac, bar.size.y)), gold if frac > 0.3 else Color("#ff5a5f"))

	var center := Vector2(w * 0.5, h * 0.42)
	draw_string(font, Vector2(0, center.y + 20), "%s = ?" % question["text"], HORIZONTAL_ALIGNMENT_CENTER, w, 56, Color.WHITE)

	for dir in 4:
		var box := Rect2(center + CHOICE_OFFSETS[dir] - CHOICE_SIZE * 0.5, CHOICE_SIZE)
		var fill := Color("#2c3560")
		if phase != Phase.ASKING and dir == question["correct"]:
			fill = Color("#2e8b47")
		draw_rect(box, fill)
		draw_rect(box, Color(1, 1, 1, 0.35), false, 2.0)
		draw_string(font, Vector2(box.position.x, box.position.y + 54), str(question["choices"][dir]),
				HORIZONTAL_ALIGNMENT_CENTER, box.size.x, 40, Color.WHITE)
		# A colored dot for every player who picked this choice.
		var dot_x := box.position.x + 14.0
		for p in player_count:
			if picks[p] == dir:
				draw_circle(Vector2(dot_x, box.position.y + 14.0), 8.0, colors[p])
				dot_x += 20.0

	var message := ""
	var message_color := Color.WHITE
	if phase != Phase.ASKING:
		if hitter != -1:
			message = "P%d vurdu! Diğerleri 1 can kaybetti." % (hitter + 1)
			message_color = colors[hitter]
		else:
			message = "Kimse bilemedi. Cevap: %d" % question["answer"]
	draw_string(font, Vector2(0, h - 150), message, HORIZONTAL_ALIGNMENT_CENTER, w, 30, message_color)

	var panel_w := w / player_count
	for p in player_count:
		var x := panel_w * p + _hit_shake(p)
		var y := h - 115.0
		var status: String = KEY_HINTS[p]
		if p < _pads.size():
			status += " / Gamepad"
		if hearts[p] <= 0:
			status = "ELENDİ"
		elif phase == Phase.ASKING and picks[p] != -1:
			status = "KİLİTLİ"
		draw_string(font, Vector2(x, y), "P%d" % (p + 1), HORIZONTAL_ALIGNMENT_CENTER, panel_w, 30, colors[p])
		var hearts_w := START_HEARTS * 26.0
		for i in START_HEARTS:
			var pos := Vector2(x + (panel_w - hearts_w) * 0.5 + 13.0 + i * 26.0, y + 24.0)
			if i < hearts[p]:
				draw_circle(pos, 9.0, colors[p])
			else:
				draw_arc(pos, 9.0, 0.0, TAU, 20, Color(1, 1, 1, 0.3), 2.0)
		draw_string(font, Vector2(x, y + 70), status, HORIZONTAL_ALIGNMENT_CENTER, panel_w, 18, dim)
		# Equipped emojis bob gently; one on cooldown sits still and dimmed.
		var can_taunt := _taunt_cooldown[p] <= 0.0
		for slot in EmojiPacks.TAUNT_SLOTS:
			var slot_x := x + panel_w * 0.5 + (slot - 1) * 70.0
			var bob := sin(_anim_time * 4.0 + slot * 1.3 + p) * 3.0 if can_taunt else 0.0
			var tint := Color.WHITE if can_taunt else Color(1, 1, 1, 0.35)
			draw_string(font, Vector2(slot_x - 35, y + 96), TAUNT_HINTS[p][slot], HORIZONTAL_ALIGNMENT_LEFT, 30, 14, dim)
			draw_string(font, Vector2(slot_x - 18, y + 98 + bob), loadouts[p][slot], HORIZONTAL_ALIGNMENT_LEFT, 40, 22, tint)

	# Thrown emojis spin along an arc to the rival's panel, then pop on impact.
	for t in taunts:
		var progress: float = t["t"]
		var from := Vector2(panel_w * (t["from"] + 0.5), h - 150.0)
		var to := Vector2(panel_w * (t["to"] + 0.5), h - 150.0)
		var pos := to
		var angle := 0.0
		var emoji_scale := 1.0
		var alpha := 1.0
		if progress < TAUNT_FLIGHT_SHARE:
			var f := progress / TAUNT_FLIGHT_SHARE
			var eased := f * f * (3.0 - 2.0 * f)
			pos = from.lerp(to, eased) + Vector2(0, -sin(f * PI) * 240.0)
			angle = sin(f * TAU * 2.0) * 0.5
			emoji_scale = lerpf(0.7, 1.4, f)
		else:
			var g := (progress - TAUNT_FLIGHT_SHARE) / (1.0 - TAUNT_FLIGHT_SHARE)
			# Squash on impact, bounce up big, then fade out.
			emoji_scale = 1.4 + sin(g * PI) * 0.9
			pos = to + Vector2(0, -absf(sin(g * PI * 2.0)) * 30.0)
			alpha = 1.0 - g * g
			for k in 6:
				var dir := Vector2.from_angle(k * TAU / 6.0)
				draw_circle(to + dir * g * 90.0, 6.0 * (1.0 - g), Color(colors[t["from"]], 1.0 - g))
		draw_set_transform(pos, angle, Vector2(emoji_scale, emoji_scale))
		draw_string(font, Vector2(-30, 16), t["emoji"], HORIZONTAL_ALIGNMENT_CENTER, 60, 44, Color(1, 1, 1, alpha))
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


## Sideways shake for a player panel that was just hit by an emoji.
func _hit_shake(player: int) -> float:
	for t in taunts:
		if t["to"] == player and t["t"] >= TAUNT_FLIGHT_SHARE:
			var g: float = (t["t"] - TAUNT_FLIGHT_SHARE) / (1.0 - TAUNT_FLIGHT_SHARE)
			return sin(g * 40.0) * 8.0 * (1.0 - g)
	return 0.0
