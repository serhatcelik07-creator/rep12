extends Node
## Game flow: main menu -> levels -> results.
## Single player: collect coins and reach the flag as fast as possible.
## 2-4 players: shared-screen race, first to the flag wins the level.
## Matematik Savaşı: 2-4 players answer math questions, last one with hearts wins.

const Level := preload("res://scripts/level.gd")
const Player := preload("res://scripts/player.gd")
const MathWar := preload("res://scripts/math_war.gd")

enum State { MENU, PLAYING, PAUSED, LEVEL_DONE, RESULTS, MATH_WAR }

const PLAYER_COLORS: Array[Color] = [Color("#ff5a5f"), Color("#3fa7ff"), Color("#5ad16b"), Color("#ffc93c")]
const MENU_ITEMS := ["Tek Oyunculu", "2 Oyuncu (Yarış)", "3 Oyuncu (Yarış)", "4 Oyuncu (Yarış)", "Matematik Savaşı", "Çıkış"]
const MATH_WAR_ITEM := 4
const LEVEL_END_DELAY := 2.5
const CAMERA_MIN_ZOOM := 0.45

var state := State.MENU
var player_count := 1
var level_index := 0
var level: Level
var players: Array[Player] = []
var scores: Array[int] = [0, 0, 0, 0]
var level_time := 0.0
var total_time := 0.0
var total_coins := 0
var total_deaths := 0
var menu_index := 0
var math_war_players := 2
var math_war: MathWar
# State to go back to when the pause menu closes.
var _resume_state := State.PLAYING
# Bumped on every level load so stale "next level" timers do nothing.
var _round := 0

var _world: Node2D
var _math_layer: CanvasLayer
var _camera: Camera2D
var _menu_label: RichTextLabel
var _hud_label: RichTextLabel
var _message_label: Label


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	RenderingServer.set_default_clear_color(Color("#1d2440"))
	_world = Node2D.new()
	_world.process_mode = Node.PROCESS_MODE_PAUSABLE
	add_child(_world)
	_camera = Camera2D.new()
	_camera.position_smoothing_enabled = true
	_camera.position_smoothing_speed = 6.0
	add_child(_camera)
	_build_ui()
	show_menu()


func _build_ui() -> void:
	# Added first so the pause message draws on top of the math war screen.
	_math_layer = CanvasLayer.new()
	add_child(_math_layer)
	var layer := CanvasLayer.new()
	add_child(layer)
	_menu_label = _make_rich_label(layer, 32)
	_menu_label.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_hud_label = _make_rich_label(layer, 22)
	_hud_label.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	_hud_label.offset_left = 16
	_hud_label.offset_top = 10
	_hud_label.offset_bottom = 50
	_message_label = Label.new()
	_message_label.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_message_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_message_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_message_label.add_theme_font_size_override("font_size", 40)
	_message_label.add_theme_constant_override("outline_size", 8)
	_message_label.add_theme_color_override("font_outline_color", Color.BLACK)
	layer.add_child(_message_label)


func _make_rich_label(parent: Node, font_size: int) -> RichTextLabel:
	var label := RichTextLabel.new()
	label.bbcode_enabled = true
	label.scroll_active = false
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_font_size_override("normal_font_size", font_size)
	label.add_theme_constant_override("outline_size", 6)
	label.add_theme_color_override("font_outline_color", Color.BLACK)
	parent.add_child(label)
	return label


# --- Menu -------------------------------------------------------------------

func show_menu() -> void:
	get_tree().paused = false
	_clear_level()
	state = State.MENU
	_hud_label.text = ""
	_message_label.text = ""
	_refresh_menu()


func _refresh_menu() -> void:
	var pads := Input.get_connected_joypads().size()
	var text := "\n\n[center][font_size=72][color=#ffcc33]ZIPZIP[/color][/font_size]\n\n"
	for i in MENU_ITEMS.size():
		var item: String = MENU_ITEMS[i]
		if i == MATH_WAR_ITEM:
			item += "  [ %d oyuncu ]" % math_war_players
		if i == menu_index:
			text += "[color=#ffcc33]> %s <[/color]\n" % item
		else:
			text += "%s\n" % item
	text += "\n[font_size=18][color=#9aa3c0]Bağlı gamepad: %d    •    Seç: Yön tuşları / D-Pad    •    Onay: Enter / A    •    Oyuncu sayısı: Sol / Sağ[/color]\n" % pads
	text += "[color=#9aa3c0]P1: WASD + Boşluk    P2: Ok tuşları    P1-P4: Gamepad 1-4[/color][/font_size][/center]"
	_menu_label.text = text


func _input(event: InputEvent) -> void:
	match state:
		State.MENU:
			if event.is_action_pressed("ui_down"):
				menu_index = (menu_index + 1) % MENU_ITEMS.size()
				_refresh_menu()
			elif event.is_action_pressed("ui_up"):
				menu_index = (menu_index - 1 + MENU_ITEMS.size()) % MENU_ITEMS.size()
				_refresh_menu()
			elif menu_index == MATH_WAR_ITEM and (event.is_action_pressed("ui_left") or event.is_action_pressed("ui_right")):
				var step := 1 if event.is_action_pressed("ui_right") else -1
				math_war_players = wrapi(math_war_players - 2 + step, 0, 3) + 2
				_refresh_menu()
			elif event.is_action_pressed("ui_accept"):
				if menu_index == MENU_ITEMS.size() - 1:
					get_tree().quit()
				elif menu_index == MATH_WAR_ITEM:
					start_math_war(math_war_players)
				else:
					start_game(menu_index + 1)
		State.PLAYING, State.MATH_WAR:
			if _is_pause_event(event):
				_set_paused(true)
		State.PAUSED:
			if _is_pause_event(event) or event.is_action_pressed("ui_accept"):
				_set_paused(false)
			elif event.is_action_pressed("ui_cancel") or _is_back_event(event):
				show_menu()
		State.RESULTS:
			if event.is_action_pressed("ui_accept"):
				show_menu()


func _is_pause_event(event: InputEvent) -> bool:
	if event is InputEventKey and event.pressed and not event.echo:
		return event.physical_keycode == KEY_ESCAPE or event.physical_keycode == KEY_P
	if event is InputEventJoypadButton and event.pressed:
		return event.button_index == JOY_BUTTON_START
	return false


func _is_back_event(event: InputEvent) -> bool:
	if event is InputEventKey and event.pressed and not event.echo:
		return event.physical_keycode == KEY_Q
	if event is InputEventJoypadButton and event.pressed:
		return event.button_index == JOY_BUTTON_BACK
	return false


func _set_paused(paused: bool) -> void:
	get_tree().paused = paused
	if paused:
		_resume_state = state
		state = State.PAUSED
		_message_label.text = "DURAKLATILDI\n\nDevam: Esc / Start / A\nAna menü: Q / Back / B"
	else:
		state = _resume_state
		_message_label.text = ""


# --- Game flow --------------------------------------------------------------

func start_game(count: int) -> void:
	player_count = count
	level_index = 0
	scores = [0, 0, 0, 0]
	total_time = 0.0
	total_coins = 0
	total_deaths = 0
	_menu_label.text = ""
	load_level()


func load_level() -> void:
	_clear_level()
	_round += 1
	level = Level.new()
	_world.add_child(level)
	level.build(Levels.DATA[level_index]["map"])
	level.flag_reached.connect(_on_flag_reached)

	var pads := Input.get_connected_joypads()
	for i in player_count:
		var player := Player.new()
		player.index = i
		player.color = PLAYER_COLORS[i]
		player.show_tag = player_count > 1
		player.joy_device = pads[i] if i < pads.size() else -1
		if player_count == 1:
			player.keys = Player.Keys.BOTH
		elif i == 0:
			player.keys = Player.Keys.WASD
		elif i == 1:
			player.keys = Player.Keys.ARROWS
		player.respawn_point = level.spawn_points[i % level.spawn_points.size()]
		player.position = player.respawn_point
		_world.add_child(player)
		players.append(player)

	_camera.limit_left = int(level.bounds.position.x)
	_camera.limit_right = int(level.bounds.end.x)
	_camera.limit_bottom = int(level.bounds.end.y)
	_camera.zoom = Vector2.ONE
	_camera.position = _camera_target()
	_camera.reset_smoothing()

	level_time = 0.0
	state = State.PLAYING
	_message_label.text = "Bölüm %d: %s" % [level_index + 1, Levels.DATA[level_index]["name"]]
	var this_round := _round
	get_tree().create_timer(1.5).timeout.connect(func() -> void:
		if _round == this_round and state == State.PLAYING:
			_message_label.text = "")


func _clear_level() -> void:
	if math_war:
		math_war.queue_free()
		math_war = null
	for player in players:
		player.queue_free()
	players.clear()
	if level:
		level.queue_free()
		level = null


func _on_flag_reached(player: Player) -> void:
	if state != State.PLAYING:
		return
	state = State.LEVEL_DONE
	for p in players:
		p.controls_enabled = false
	total_time += level_time
	for p in players:
		total_coins += p.coins
		total_deaths += p.deaths
	if player_count == 1:
		_message_label.text = "Bölüm tamamlandı!\nSüre: %.1f sn   Altın: %d/%d" % [level_time, player.coins, level.coin_total]
	else:
		scores[player.index] += 1
		_message_label.text = "P%d bölümü kazandı!" % (player.index + 1)
		_message_label.add_theme_color_override("font_color", player.color)
	var this_round := _round
	get_tree().create_timer(LEVEL_END_DELAY, false).timeout.connect(func() -> void:
		if _round == this_round and state == State.LEVEL_DONE:
			_next_level())


func _next_level() -> void:
	_message_label.remove_theme_color_override("font_color")
	level_index += 1
	if level_index < Levels.DATA.size():
		load_level()
	else:
		_show_results()


func _show_results() -> void:
	_clear_level()
	state = State.RESULTS
	_hud_label.text = ""
	_message_label.text = ""
	var text := "\n\n\n[center][font_size=56][color=#ffcc33]OYUN BİTTİ[/color][/font_size]\n\n"
	if player_count == 1:
		text += "Toplam süre: %.1f sn\nAltın: %d\nÖlüm: %d\n" % [total_time, total_coins, total_deaths]
	else:
		var best := 0
		for i in player_count:
			if scores[i] > scores[best]:
				best = i
		for i in player_count:
			text += "[color=#%s]P%d: %d bölüm[/color]\n" % [PLAYER_COLORS[i].to_html(false), i + 1, scores[i]]
		text += "\n[color=#%s]Kazanan: P%d![/color]\n" % [PLAYER_COLORS[best].to_html(false), best + 1]
	text += "\n[font_size=20][color=#9aa3c0]Ana menü için Enter / A[/color][/font_size][/center]"
	_menu_label.text = text


# --- Matematik Savaşı -------------------------------------------------------

func start_math_war(count: int, seed_value: int = 0) -> void:
	_clear_level()
	player_count = count
	_menu_label.text = ""
	_hud_label.text = ""
	_message_label.text = ""
	math_war = MathWar.new()
	math_war.process_mode = Node.PROCESS_MODE_PAUSABLE
	_math_layer.add_child(math_war)
	math_war.setup(count, PLAYER_COLORS, seed_value)
	math_war.finished.connect(_on_math_war_finished)
	state = State.MATH_WAR


func _on_math_war_finished(winner: int, hearts: Array) -> void:
	_clear_level()
	state = State.RESULTS
	var text := "\n\n\n[center][font_size=56][color=#ffcc33]SAVAŞ BİTTİ[/color][/font_size]\n\n"
	for i in hearts.size():
		text += "[color=#%s]P%d: %d can[/color]\n" % [PLAYER_COLORS[i].to_html(false), i + 1, hearts[i]]
	if winner == -1:
		text += "\nBerabere!\n"
	else:
		text += "\n[color=#%s]Kazanan: P%d![/color]\n" % [PLAYER_COLORS[winner].to_html(false), winner + 1]
	text += "\n[font_size=20][color=#9aa3c0]Ana menü için Enter / A[/color][/font_size][/center]"
	_menu_label.text = text


# --- Per-frame updates ------------------------------------------------------

func _physics_process(_delta: float) -> void:
	if state != State.PLAYING or not level:
		return
	for player in players:
		if player.position.y > level.bounds.end.y + 64.0:
			player.die()
	if player_count > 1:
		_pull_stragglers()


func _process(delta: float) -> void:
	if state != State.PLAYING and state != State.LEVEL_DONE:
		return
	if state == State.PLAYING:
		level_time += delta
	_update_camera(delta)
	_update_hud()


func _camera_target() -> Vector2:
	var sum := Vector2.ZERO
	for player in players:
		sum += player.position
	return sum / maxf(players.size(), 1)


func _update_camera(delta: float) -> void:
	_camera.position = _camera_target()
	if player_count == 1:
		return
	# Zoom out so every player fits on the shared screen.
	var box := Rect2(players[0].position, Vector2.ZERO)
	for player in players:
		box = box.expand(player.position)
	var view := get_viewport().get_visible_rect().size
	var fit := minf(view.x / (box.size.x + 400.0), view.y / (box.size.y + 300.0))
	var zoom := clampf(fit, CAMERA_MIN_ZOOM, 1.0)
	_camera.zoom = _camera.zoom.lerp(Vector2(zoom, zoom), clampf(delta * 3.0, 0.0, 1.0))


func _pull_stragglers() -> void:
	# A player who falls too far behind is moved to the leader, so nobody is lost off-screen.
	var view := get_viewport().get_visible_rect().size / CAMERA_MIN_ZOOM
	var leader := players[0]
	for player in players:
		if player.position.x > leader.position.x:
			leader = player
	for player in players:
		if player != leader and leader.position.x - player.position.x > view.x * 0.9:
			player.position = leader.position + Vector2(0, -40)
			player.velocity = Vector2.ZERO


func _update_hud() -> void:
	var text := "Bölüm %d/%d   " % [level_index + 1, Levels.DATA.size()]
	if player_count == 1:
		var player := players[0]
		text += "Altın %d/%d   Süre %.1f   Ölüm %d" % [player.coins, level.coin_total, level_time, player.deaths]
	else:
		for player in players:
			text += "[color=#%s]P%d: %d[/color]   " % [player.color.to_html(false), player.index + 1, scores[player.index]]
	_hud_label.text = text
