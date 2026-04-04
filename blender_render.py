import bpy
import mathutils
import math
import sys

SITE = r"C:\Users\Thomas Vuong\Desktop\dielaughing-website"

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def get_bounds(scene):
    mn = [float('inf')]*3
    mx = [float('-inf')]*3
    for obj in scene.objects:
        if obj.type == 'MESH':
            for c in obj.bound_box:
                w = obj.matrix_world @ mathutils.Vector(c)
                for i in range(3):
                    mn[i] = min(mn[i], w[i])
                    mx[i] = max(mx[i], w[i])
    return mn, mx

def setup_render(scene, w, h, outpath):
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.eevee.taa_render_samples = 32
    scene.render.film_transparent = True
    scene.render.resolution_x = w
    scene.render.resolution_y = h
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.filepath = outpath

def add_camera(loc, target, lens=85):
    cam = bpy.data.cameras.new("Cam")
    cam.lens = lens
    obj = bpy.data.objects.new("Cam", cam)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.scene.camera = obj
    obj.location = loc
    # Look from +X toward target with Z as world up
    obj.rotation_euler = (math.pi/2, 0, math.pi/2)
    return obj

def add_light(name, kind, energy, color, loc, size=2.0):
    d = bpy.data.lights.new(name, kind)
    d.energy = energy
    d.color = color
    if kind == 'AREA': d.size = size
    o = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    return o

# ── RENDER 1: Skeleton logo ─────────────────────────────────────────────────
print("\n=== Rendering skeleton ===")
clear_scene()
bpy.ops.import_scene.gltf(filepath=r"C:\Users\Thomas Vuong\Downloads\skeleton comedian 3d model.glb")

mn, mx = get_bounds(bpy.context.scene)
cx = (mn[0]+mx[0])/2; cy = (mn[1]+mx[1])/2; cz = (mn[2]+mx[2])/2
print(f"X:{mn[0]:.3f}→{mx[0]:.3f}  Y:{mn[1]:.3f}→{mx[1]:.3f}  Z:{mn[2]:.3f}→{mx[2]:.3f}")

# Face is flat in YZ, pointing in ±X. Camera from +X side.
dist = 2.4
add_camera((cx + dist, cy, cz), (cx, cy, cz), lens=85)
add_light("Key",  'AREA', 800, (1.0,1.0,1.0),   (cx+2, cy-1.5, cz+1.5), 2)
add_light("Fill", 'AREA', 300, (0.75,0.2,1.0),  (cx+2, cy+2.0, cz+0.5), 2)
add_light("Rim",  'AREA', 220, (1.0,0.28,0.6),  (cx-1, cy,     cz+1.0), 1)
add_light("Top",  'AREA', 250, (1.0,1.0,1.0),   (cx+1, cy,     cz+2.0), 1)

setup_render(bpy.context.scene, 800, 800, SITE + r"\skeleton-logo.png")
bpy.ops.render.render(write_still=True)
print("Saved skeleton-logo.png")

# ── RENDER 2: Enter patch ───────────────────────────────────────────────────
print("\n=== Rendering patch ===")
clear_scene()
bpy.ops.import_scene.gltf(filepath=r"C:\Users\Thomas Vuong\Downloads\embroidered patch 3d model.glb")

mn, mx = get_bounds(bpy.context.scene)
cx = (mn[0]+mx[0])/2; cy = (mn[1]+mx[1])/2; cz = (mn[2]+mx[2])/2
print(f"X:{mn[0]:.3f}→{mx[0]:.3f}  Y:{mn[1]:.3f}→{mx[1]:.3f}  Z:{mn[2]:.3f}→{mx[2]:.3f}")

dist = 2.4
add_camera((cx + dist, cy, cz), (cx, cy, cz), lens=85)
add_light("Key",  'AREA', 800, (1.0,1.0,1.0),   (cx+2, cy-1.5, cz+1.5), 2)
add_light("Fill", 'AREA', 300, (0.75,0.2,1.0),  (cx+2, cy+2.0, cz+0.5), 2)
add_light("Rim",  'AREA', 220, (1.0,0.28,0.6),  (cx-1, cy,     cz+1.0), 1)
add_light("Top",  'AREA', 250, (1.0,1.0,1.0),   (cx+1, cy,     cz+2.0), 1)

setup_render(bpy.context.scene, 900, 500, SITE + r"\enter-patch.png")
bpy.ops.render.render(write_still=True)
print("Saved enter-patch.png")

print("\n=== ALL DONE ===")
