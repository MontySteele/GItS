# Editor-side probe evidence

Produced by `tools/animation_bakeoff/export_bakeoff.ps1`, which loads each
scene in the headless MegaDot 4.5.1 editor and walks it. Live capture was
NOT available for this run (the game was in use), so this is the strongest
runtime evidence the lane has -- it proves the scene loads, instantiates,
and carries the animations, states, and rig nodes claimed for it. It does
NOT prove anything about how the motion looks.

## layered

```
PROBE|scene=res://sprig/layered.tscn
PROBE|nodes=17
PROBE|dependencies=8
PROBE|dependency=res://sprig/art/sprig_shadow.png
PROBE|dependency=res://sprig/art/sprig_leg_back.png
PROBE|dependency=res://sprig/art/sprig_arm_back.png
PROBE|dependency=res://sprig/art/sprig_leg_front.png
PROBE|dependency=res://sprig/art/sprig_torso.png
PROBE|dependency=res://sprig/art/sprig_head.png
PROBE|dependency=res://sprig/art/sprig_arm_front.png
PROBE|dependency=res://sprig/art/sprig_prop.png
PROBE|animations=6
PROBE|animation=RESET|length=0.0010000000475|tracks=17|loop=0
PROBE|animation=attack|length=0.5|tracks=5|loop=0
PROBE|animation=death|length=1.0|tracks=6|loop=0
PROBE|animation=hurt|length=0.40000000596046|tracks=4|loop=0
PROBE|animation=idle|length=2.40000009536743|tracks=7|loop=1
PROBE|animation=intent|length=0.89999997615814|tracks=5|loop=1
PROBE|states=7
PROBE|state=End
PROBE|state=Start
PROBE|state=attack
PROBE|state=death
PROBE|state=hurt
PROBE|state=idle
PROBE|state=intent
PROBE|missing_dependencies=0
PROBE|sprites=8
PROBE|bone2d=0
PROBE|polygons=0
PROBE|skinned_polygons=0
PROBE|emitters=0
PROBE|ok=1
```

## cutout

```
PROBE|scene=res://sprig/cutout.tscn
PROBE|nodes=27
PROBE|dependencies=8
PROBE|dependency=res://sprig/art/sprig_shadow.png
PROBE|dependency=res://sprig/art/sprig_leg_back.png
PROBE|dependency=res://sprig/art/sprig_arm_back.png
PROBE|dependency=res://sprig/art/sprig_leg_front.png
PROBE|dependency=res://sprig/art/sprig_torso.png
PROBE|dependency=res://sprig/art/sprig_head.png
PROBE|dependency=res://sprig/art/sprig_arm_front.png
PROBE|dependency=res://sprig/art/sprig_prop.png
PROBE|animations=6
PROBE|animation=RESET|length=0.0010000000475|tracks=17|loop=0
PROBE|animation=attack|length=0.5|tracks=5|loop=0
PROBE|animation=death|length=1.0|tracks=6|loop=0
PROBE|animation=hurt|length=0.40000000596046|tracks=4|loop=0
PROBE|animation=idle|length=2.40000009536743|tracks=7|loop=1
PROBE|animation=intent|length=0.89999997615814|tracks=5|loop=1
PROBE|states=7
PROBE|state=End
PROBE|state=Start
PROBE|state=attack
PROBE|state=death
PROBE|state=hurt
PROBE|state=idle
PROBE|state=intent
PROBE|missing_dependencies=0
PROBE|sprites=8
PROBE|bone2d=9
PROBE|polygons=0
PROBE|skinned_polygons=0
PROBE|emitters=0
PROBE|ok=1
```

## mesh

```
PROBE|scene=res://sprig/mesh.tscn
PROBE|nodes=27
PROBE|dependencies=8
PROBE|dependency=res://sprig/art/sprig_shadow.png
PROBE|dependency=res://sprig/art/sprig_leg_back.png
PROBE|dependency=res://sprig/art/sprig_arm_back.png
PROBE|dependency=res://sprig/art/sprig_leg_front.png
PROBE|dependency=res://sprig/art/sprig_torso.png
PROBE|dependency=res://sprig/art/sprig_head.png
PROBE|dependency=res://sprig/art/sprig_arm_front.png
PROBE|dependency=res://sprig/art/sprig_prop.png
PROBE|animations=6
PROBE|animation=RESET|length=0.0010000000475|tracks=16|loop=0
PROBE|animation=attack|length=0.5|tracks=5|loop=0
PROBE|animation=death|length=1.0|tracks=6|loop=0
PROBE|animation=hurt|length=0.40000000596046|tracks=4|loop=0
PROBE|animation=idle|length=2.40000009536743|tracks=6|loop=1
PROBE|animation=intent|length=0.89999997615814|tracks=5|loop=1
PROBE|states=7
PROBE|state=End
PROBE|state=Start
PROBE|state=attack
PROBE|state=death
PROBE|state=hurt
PROBE|state=idle
PROBE|state=intent
PROBE|missing_dependencies=0
PROBE|sprites=0
PROBE|bone2d=9
PROBE|polygons=8
PROBE|skinned_polygons=8
PROBE|emitters=0
PROBE|ok=1
```

## particles

```
PROBE|scene=res://sprig/particles.tscn
PROBE|nodes=13
PROBE|dependencies=2
PROBE|dependency=res://sprig/art/sprig_composite.png
PROBE|dependency=res://sprig/art/sprig_mote.png
PROBE|animations=6
PROBE|animation=RESET|length=0.0010000000475|tracks=9|loop=0
PROBE|animation=attack|length=0.5|tracks=3|loop=0
PROBE|animation=death|length=1.0|tracks=4|loop=0
PROBE|animation=hurt|length=0.40000000596046|tracks=2|loop=0
PROBE|animation=idle|length=2.40000009536743|tracks=1|loop=1
PROBE|animation=intent|length=0.89999997615814|tracks=2|loop=1
PROBE|states=7
PROBE|state=End
PROBE|state=Start
PROBE|state=attack
PROBE|state=death
PROBE|state=hurt
PROBE|state=idle
PROBE|state=intent
PROBE|missing_dependencies=0
PROBE|sprites=1
PROBE|bone2d=0
PROBE|polygons=0
PROBE|skinned_polygons=0
PROBE|emitters=3
PROBE|ok=1
```
