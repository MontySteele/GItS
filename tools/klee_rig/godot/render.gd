extends SceneTree

# Klee combat scene renderer (tools/klee_rig/render.py copies this into a
# scratch project and runs it WITH a window: under --headless nothing draws).
#
# Job JSON (first user arg): {"passes": [{"scene": "res://...", "out": "<dir>",
#   "prefix": "x", "scale": 1, "w": 300, "h": 340, "origin": [150, 320],
#   "facing": 1, "jobs": [["idle", [0.0, 0.3, ...]], ...]}, ...]}
# Each frame is posed by RESET, then the animation sought to t and paused;
# the AnimationTree is switched off so the player is the only writer.

var job


func _initialize() -> void:
	var f = FileAccess.open(OS.get_cmdline_user_args()[0], FileAccess.READ)
	job = JSON.parse_string(f.get_as_text())
	_run.call_deferred()


func _run() -> void:
	for pass_cfg in job["passes"]:
		await _pass(pass_cfg)
	print("RENDER|done")
	quit(0)


func _pass(cfg) -> void:
	var vp := SubViewport.new()
	vp.size = Vector2i(int(cfg["w"]), int(cfg["h"]))
	vp.transparent_bg = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(vp)
	var inst = (ResourceLoader.load(cfg["scene"]) as PackedScene).instantiate()
	vp.add_child(inst)
	await process_frame
	var s := float(cfg["scale"])
	vp.canvas_transform = Transform2D(0.0, Vector2(s, s), 0.0, Vector2(cfg["origin"][0], cfg["origin"][1]))
	var tree = inst.get_node_or_null("AnimationTree")
	if tree:
		tree.active = false
	var player: AnimationPlayer = inst.get_node("AnimationPlayer")
	var facing = inst.get_node_or_null("Visuals/Facing")
	if facing:
		facing.scale = Vector2(float(cfg.get("facing", 1.0)), 1.0)
	for entry in cfg["jobs"]:
		var anim: String = entry[0]
		var times = entry[1]
		for i in range(times.size()):
			player.play("RESET")
			player.seek(0.0, true)
			player.stop()
			if anim != "RESET":
				player.play(anim)
				player.seek(float(times[i]), true)
				player.pause()
			await process_frame
			await process_frame
			await RenderingServer.frame_post_draw
			var img = vp.get_texture().get_image()
			img.save_png("%s/%s%s_%03d.png" % [cfg["out"], cfg["prefix"], anim, i])
	vp.queue_free()
	await process_frame
