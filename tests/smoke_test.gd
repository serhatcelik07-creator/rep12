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

	# Matematik Savaşı
	var gen := RandomNumberGenerator.new()
	gen.seed = 7
	var questions_ok := true
	for level in 40:
		var q: Dictionary = main.MathWar.make_question(level, gen)
		var choices: Array = q["choices"]
		var unique := {}
		for c in choices:
			unique[c] = true
		if choices.size() != 4 or unique.size() != 4 or choices[q["correct"]] != q["answer"]:
			questions_ok = false
			print("      bad question: %s" % q)
	check(questions_ok, "math questions have 4 distinct choices incl. the answer")

	main.show_menu()
	await frames(5)
	main.start_math_war(3, 42)
	await frames(2)
	var mw = main.math_war
	check(main.state == main.State.MATH_WAR and str(mw.hearts) == "[5, 5, 5]", "math war starts with 3 players, 5 hearts each")
	var right: int = mw.question["correct"]
	mw.answer(1, (right + 1) % 4)
	check(mw.hearts[1] == 4 and mw.phase == mw.Phase.ASKING, "wrong answer costs a heart, question stays open")
	mw.answer(1, right)
	check(mw.hitter == -1, "locked-out player can't answer again")
	mw.answer(0, right)
	check(mw.hitter == 0 and str(mw.hearts) == "[5, 3, 4]", "first correct answer hits the others")
	var thrown := []
	mw.taunted.connect(func(from: int, to: int, emoji: String) -> void: thrown.append([from, to, emoji]))
	check(mw.taunt(1, 0) and mw.taunts.size() == 1, "P2 throws an emoji")
	check(thrown.size() == 1 and thrown[0][1] == 0 and thrown[0][2] == mw.loadouts[1][0], "emoji flies at the rival with most hearts")
	check(not mw.taunt(1, 1), "emoji taunts have a cooldown")
	key(KEY_E, true)
	key(KEY_E, false)
	check(thrown.size() == 2 and thrown[1][0] == 0 and thrown[1][1] == 2, "P1 throws with the E key")
	await frames(5)
	check(mw.taunts[0]["t"] > 0.0, "thrown emojis animate")
	await create_timer(mw.REVEAL_TIME + 0.3).timeout
	check(mw.question_number == 2 and mw.phase == mw.Phase.ASKING, "next question after reveal")
	check(mw.taunts.is_empty(), "emoji animations finish")
	key(KEY_I, true)
	key(KEY_I, false)
	check(mw.picks[2] == 0, "P3 answers with IJKL keys")
	mw.hearts[1] = 0
	mw.hearts[2] = 0
	mw.answer(0, mw.question["correct"])
	await create_timer(mw.REVEAL_TIME + 0.3).timeout
	await frames(2)
	check(main.state == main.State.RESULTS, "math war ends when one player is left")

	print("\n%s (%d failures)" % ["ALL PASSED" if failures == 0 else "FAILED", failures])
	quit(1 if failures else 0)


func _find_flag(level) -> Vector2:
	for c in level.get_children():
		if c.get("kind") == 3:
			return c.position
	return Vector2.ZERO
