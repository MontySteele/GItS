extends SceneTree

# Klee mesh rig probe (tools/klee_rig/verify.py copies this into a scratch
# project). Loads the generated scene in the engine and prints PROBE| lines;
# exits non-zero when a skinned polygon came out with no bones, which is the
# silent failure the bake-off found (a `bones/0/path` line is dropped by the
# parser and get_bone_count() reads 0 with every step green).
#
# Checks run on the first process frame: Skeleton2D.get_bone_count() errors
# during _initialize (tools/skeleton2d_spike/README.md).

var scene_path := ""
var inst: Node
var frames := 0
var failures := 0


func _initialize() -> void:
	scene_path = OS.get_cmdline_user_args()[0]
	var packed = ResourceLoader.load(scene_path)
	if packed == null:
		print("PROBE|error=scene_load_failed")
		quit(2)
		return
	inst = packed.instantiate()
	root.add_child(inst)


func _fail(msg: String) -> void:
	failures += 1
	print("PROBE|FAIL|", msg)


func _process(_delta: float) -> bool:
	frames += 1
	if frames < 2:
		return false
	var skel = inst.get_node_or_null("Visuals/Facing/Rig/Skeleton") as Skeleton2D
	if skel == null:
		_fail("no Skeleton2D")
	else:
		print("PROBE|skeleton_bones=", skel.get_bone_count())
	for layer in ["Smoke", "Floaters", "Dumpty", "Body", "Dodoco"]:
		var poly = inst.get_node_or_null("Visuals/Facing/Rig/" + layer) as Polygon2D
		if poly == null:
			_fail("missing Polygon2D " + layer)
			continue
		var n = poly.polygon.size()
		var bc = poly.get_bone_count()
		var bad = 0
		for i in range(bc):
			if poly.get_bone_weights(i).size() != n:
				bad += 1
			var bone = poly.get_node_or_null(poly.skeleton).get_node_or_null(poly.get_bone_path(i))
			if not (bone is Bone2D):
				bad += 1
		print("PROBE|polygon=", layer, "|vertices=", n, "|uv=", poly.uv.size(), "|polygons=", poly.polygons.size(), "|bones=", bc, "|bad=", bad)
		if bc == 0:
			_fail(layer + " has no bones")
		if bad > 0:
			_fail(layer + " has bad bone entries")
		if poly.uv.size() != n:
			_fail(layer + " uv count != vertex count")
	for path in ["Visuals", "Visuals/Facing", "Visuals/Facing/Rig", "Bounds", "CenterPos", "IntentPos", "AnimationPlayer", "AnimationTree"]:
		if inst.get_node_or_null(path) == null:
			_fail("missing node " + path)
	var player = inst.get_node_or_null("AnimationPlayer") as AnimationPlayer
	if player:
		for a in player.get_animation_list():
			var anim = player.get_animation(a)
			var dead = 0
			for t in range(anim.get_track_count()):
				var p = anim.track_get_path(t)
				var node = inst.get_node_or_null(NodePath(String(p.get_concatenated_names())))
				if node == null:
					dead += 1
			print("PROBE|animation=", a, "|length=", anim.length, "|tracks=", anim.get_track_count(), "|dead_tracks=", dead)
			if dead > 0:
				_fail("animation " + a + " has tracks to missing nodes")
	var tree = inst.get_node_or_null("AnimationTree") as AnimationTree
	if tree:
		var sm = tree.tree_root as AnimationNodeStateMachine
		for s in ["idle", "attack", "hurt", "death", "cast", "power", "idle_low", "setoff"]:
			if not sm.has_node(s):
				_fail("state machine lacks " + s)
		_drive(tree)
	_merchant()
	print("PROBE|failures=", failures)
	quit(1 if failures > 0 else 0)
	return true


func _alpha(path: String, prop: String) -> float:
	var n = inst.get_node_or_null(path)
	if n == null:
		_fail("missing " + path)
		return -1.0
	return (n.get(prop) as Color).a


func _state(tree: AnimationTree, label: String, sheet: String, frame: int, rig_a: float, model_a: float) -> void:
	# Which sheet shows, at which frame, and whether the splash rig or the
	# model is the visible figure: the tree's own blend, read back.
	var shown := []
	for s in ["Idle", "IdleLow", "Attack", "Hurt", "Death", "Cast"]:
		if _alpha("Visuals/Facing/Model/" + s, "self_modulate") > 0.5:
			shown.append(s)
	var spr = inst.get_node_or_null("Visuals/Facing/Model/" + sheet) as Sprite2D
	var f = spr.frame if spr else -1
	var ra = _alpha("Visuals/Facing/Rig", "modulate")
	var ma = _alpha("Visuals/Facing/Model", "modulate")
	var pb = tree.get("parameters/playback") as AnimationNodeStateMachinePlayback
	print("PROBE|drive=", label, "|state=", pb.get_current_node(), "|shown=", ",".join(shown), "|frame=", f,
		"|rig_a=", snappedf(ra, 0.01), "|model_a=", snappedf(ma, 0.01))
	if shown != [sheet]:
		_fail(label + ": expected only " + sheet + " visible, got " + str(shown))
	if frame >= 0 and f != frame:
		_fail(label + ": " + sheet + " frame " + str(f) + " != " + str(frame))
	if rig_a >= 0.0 and (abs(ra - rig_a) > 0.05 or abs(ma - model_a) > 0.05):
		_fail(label + ": rig/model alpha " + str(ra) + "/" + str(ma))


func _step(tree: AnimationTree, seconds: float) -> void:
	# The game ticks the tree once a frame; one large advance() straight
	# after travel() is not what it ever sees.
	var n = int(round(seconds * 60.0))
	for i in range(n):
		tree.advance(1.0 / 60.0)


func _drive(tree: AnimationTree) -> void:
	var pb = tree.get("parameters/playback") as AnimationNodeStateMachinePlayback
	_step(tree, 0.53)
	_state(tree, "idle@0.53", "Idle", 10, 0.0, 1.0)
	pb.travel("attack")
	_step(tree, 0.48)
	_state(tree, "attack@0.48", "Attack", 9, 0.0, 1.0)
	_step(tree, 0.7)
	_state(tree, "attack->idle", "Idle", -1, 0.0, 1.0)
	pb.travel("hurt")
	_step(tree, 0.25)
	_state(tree, "hurt@0.25", "Hurt", 4, 0.0, 1.0)
	_step(tree, 0.8)
	pb.travel("setoff")
	_step(tree, 0.5)
	_state(tree, "setoff@0.5", "Idle", 0, 1.0, 0.0)
	pb.travel("attack")
	_step(tree, 0.1)
	_state(tree, "setoff->attack (the router, not the tree, absorbs this)", "Attack", -1, -1.0, -1.0)
	_step(tree, 1.2)
	pb.travel("death")
	_step(tree, 1.47)
	_state(tree, "death@1.47", "Death", 28, 0.0, 1.0)


func _merchant() -> void:
	var packed = ResourceLoader.load("res://klee/model/merchant_character.tscn")
	if packed == null:
		_fail("merchant scene failed to load")
		return
	var m = packed.instantiate()
	root.add_child(m)
	var ap = m.get_node_or_null("AnimationPlayer") as AnimationPlayer
	var sheet = m.get_node_or_null("Sheet") as Sprite2D
	if ap == null or sheet == null or sheet.texture == null:
		_fail("merchant scene lacks its player or sheet")
		return
	ap.advance(0.75)
	print("PROBE|merchant|playing=", ap.current_animation, "|frame=", sheet.frame, "|tex=", sheet.texture.get_size())
	if ap.current_animation != "relaxed_loop" or sheet.frame != 7:
		_fail("merchant idle is not autoplaying")
