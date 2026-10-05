extends SceneTree
## Headless smoke test: godot --headless --script res://tests/smoke_test.gd

var failures := 0


func _initialize() -> void:
	_run.call_deferred()


func check(cond: bool, msg: String) -> void:
	print(("PASS  " if cond else "FAIL  ") + msg)
	if not cond:
		failures += 1


func frames(n: int) -> void:
	for i in n:
		await physics_frame


func key(code: Key, down: bool) -> void:
	var ev := InputEventKey.new()
	ev.physical_keycode = code
	ev.keycode = code
	ev.pressed = down
	Input.parse_input_event(ev)
	Input.flush_buffered_events()


func _run() -> void:
	var main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await frames(5)
	check(main.state == main.State.MENU, "starts in menu")

	main.start_game(1)
	await frames(60)
	var p = main.players[0]
	check(p.is_on_floor(), "player lands on ground")

	var x0: float = p.position.x
	key(KEY_D, true)
	await frames(30)
	key(KEY_D, false)
	check(p.position.x > x0 + 50, "player walks right with D (%.0f -> %.0f)" % [x0, p.position.x])

	await frames(30)
	var y0: float = p.position.y
	var top := y0
	key(KEY_SPACE, true)
	for i in 50:
		await physics_frame
		top = minf(top, p.position.y)
	key(KEY_SPACE, false)
	await frames(40)
	print("      jump height: %.0f px" % (y0 - top))
	check(y0 - top > 80 and y0 - top < 120, "full jump is ~3 tiles high")
	check(p.is_on_floor(), "player lands after jump")

	# Fall into a pit -> respawn
	p.position = Vector2(31.5 * 32, 12 * 32)
	await frames(90)
	check(p.deaths == 1, "falling into a pit counts a death")
	check(p.position.distance_to(p.respawn_point) < 64, "player respawns")

	# Play through all levels by touching the flag
	for i in Levels.DATA.size():
		check(main.level_index == i and main.state == main.State.PLAYING, "level %d loaded" % (i + 1))
		var flag := _find_flag(main.level)
		p = main.players[0]
		p.position = flag
		await frames(10)
		check(main.state == main.State.LEVEL_DONE, "flag finishes level %d" % (i + 1))
		await create_timer(main.LEVEL_END_DELAY + 0.3).timeout
		await frames(2)
	check(main.state == main.State.RESULTS, "results screen after last level")

	# 4-player race
	main.show_menu()
	await frames(5)
	main.start_game(4)
	await frames(60)
	check(main.players.size() == 4, "4 players spawned")
	var on_floor := 0
	for pl in main.players:
		if pl.is_on_floor():
			on_floor += 1
	check(on_floor >= 3, "players stand on ground or each other (%d on floor)" % on_floor)
	main.players[2].position = _find_flag(main.level)
	await frames(10)
	check(main.scores[2] == 1, "P3 wins the round")

	print("\n%s (%d failures)" % ["ALL PASSED" if failures == 0 else "FAILED", failures])
	quit(1 if failures else 0)


func _find_flag(level) -> Vector2:
	for c in level.get_children():
		if c.get("kind") == 3:
			return c.position
	return Vector2.ZERO
