"""Блокаут ассета в Blender без GUI: примитив по размеру → материалы по ролям → LOD → (клип) → GLB → турнтейбл.

Запуск (Blender 4.2+ / 5.x, bpy):
  blender --background --factory-startup --python blender_blockout.py -- \
    --id mdl_lantern_base_lit --shape cylinder --size 0.6x0.6x1 --colors "#F2B84B,#2B2D42" \
    --out Assets/_Project/Art/Models/mdl_lantern_base_lit.glb [--blend art-source/<ID>.blend] \
    [--lod 0.5,0.25] [--turntable design/art/models/<ID>] [--engine eevee|workbench] [--clip idle:24 --fps 30]

--size — X×Y×Z в метрах (Z вверх в Blender = Y вверх в glTF). Масштаб применяется (GL8), имя объекта = ID (GL3),
LOD — копии с Decimate (<ID>_LOD1…, LOD0 переименовывается в <ID>_LOD0). --clip name:frames — простой клип
(покачивание) для проверки пути анимации, не финальная анимация. Платные генераторы не вызываются.
"""
import argparse
import math
import sys
from pathlib import Path

import bpy

SHAPES = {
    "cube": lambda: bpy.ops.mesh.primitive_cube_add(size=1),
    "cylinder": lambda: bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.5, depth=1),
    "sphere": lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.5),
    "capsule": lambda: bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.5, depth=1),
    "cone": lambda: bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.5, depth=1),
}


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--shape", default="cube", choices=sorted(SHAPES))
    ap.add_argument("--size", default="1x1x1")
    ap.add_argument("--colors", default="#808080")
    ap.add_argument("--out", required=True)
    ap.add_argument("--blend", default=None)
    ap.add_argument("--lod", default="")
    ap.add_argument("--turntable", default=None)
    ap.add_argument("--engine", default="eevee", choices=["eevee", "workbench"])
    ap.add_argument("--res", type=int, default=512)
    ap.add_argument("--clip", default=None)
    ap.add_argument("--fps", type=int, default=30)
    return ap.parse_args(argv)


def hex_rgba(h):
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1.0,)


def material(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.7
    m.diffuse_color = rgba
    return m


def main():
    a = args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = a.fps
    sx, sy, sz = (float(v) for v in a.size.lower().replace("×", "x").split("x"))

    SHAPES[a.shape]()
    obj = bpy.context.active_object
    obj.name = obj.data.name = a.id
    obj.scale = (sx, sy, sz)
    obj.location.z = sz / 2                     # опора на землю
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.shade_flat()

    colors = [c for c in a.colors.split(",") if c.strip()]
    for i, c in enumerate(colors):
        obj.data.materials.append(material(f"{a.id}_role{i}", hex_rgba(c)))
    if len(colors) > 1:                          # верхняя треть (меш центрирован в 0) — второй цвет роли
        for p in obj.data.polygons:
            p.material_index = 1 if p.center.z > sz / 6 else 0

    if a.clip:
        name, frames = a.clip.split(":")
        frames = int(frames)
        obj.animation_data_create()
        action = bpy.data.actions.new(name)
        obj.animation_data.action = action
        for f, z in ((1, sz / 2), (1 + frames // 2, sz / 2 + 0.1 * sz), (1 + frames, sz / 2)):
            obj.location.z = z
            obj.keyframe_insert("location", index=2, frame=f)
        obj.location.z = sz / 2
        scene.frame_start, scene.frame_end = 1, 1 + frames

    lods = [float(r) for r in a.lod.split(",") if r.strip()]
    if lods:
        obj.name = obj.data.name = f"{a.id}_LOD0"
        for i, ratio in enumerate(lods, 1):
            dup = obj.copy()
            dup.data = obj.data.copy()
            dup.animation_data_clear()
            dup.name = dup.data.name = f"{a.id}_LOD{i}"
            scene.collection.objects.link(dup)
            mod = dup.modifiers.new("Decimate", "DECIMATE")
            mod.ratio = ratio
            bpy.context.view_layer.objects.active = dup
            bpy.ops.object.modifier_apply(modifier=mod.name)
            dup.hide_render = True

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out), export_format="GLB", export_apply=True,
                              export_animations=bool(a.clip), export_yup=True)
    print(f"GLB: {out.resolve()}")
    if a.blend:
        Path(a.blend).parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(a.blend).resolve()))

    if a.turntable:
        td = Path(a.turntable)
        td.mkdir(parents=True, exist_ok=True)
        engines = ["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"] if a.engine == "eevee" else []
        for e in engines + ["BLENDER_WORKBENCH"]:
            try:
                scene.render.engine = e
                break
            except TypeError:
                continue
        scene.render.resolution_x = scene.render.resolution_y = a.res
        scene.render.film_transparent = False
        world = bpy.data.worlds.new("gd_world")
        world.color = (0.5, 0.5, 0.5)
        scene.world = world
        r = max(sx, sy, sz) * 2.2
        bpy.ops.object.camera_add(location=(0, -r, sz * 0.5 + r * 0.35))
        cam = bpy.context.active_object
        cam.rotation_euler = (math.atan2(r, r * 0.35) , 0, 0)
        scene.camera = cam
        bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30)))
        bpy.context.active_object.data.energy = 3
        scene.frame_set(scene.frame_start)
        for i in range(8):
            obj.rotation_euler.z = math.radians(45 * i)
            scene.render.filepath = str((td / f"turntable_{i + 1:02d}.png").resolve())
            bpy.ops.render.render(write_still=True)
        obj.rotation_euler.z = 0
        print(f"Турнтейбл: {td.resolve()} (8 кадров, {scene.render.engine})")


main()
