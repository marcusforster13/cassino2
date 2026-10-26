"""Cassino clandestino - exporta o freezer horizontal (bau branco atras do balcao) para o autor refazer.
Uso: blender -b ../cassino.blend --python exportar_freezer.py  ->  para_editar/freezer_horizontal.glb
Sai centrado, base em z = 0, na orientacao da cena: 70 cm em X, 1,50 m em Y (comprido ao longo da parede), 90 cm de
altura; a parede fica do lado +X e o balcao do lado -X."""
import bpy, os
from mathutils import Matrix
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
pecas = [o for o in bpy.data.objects if o.type == "MESH" and o.name.split(".")[0] in ("Freezer_Horizontal",)]
for o in pecas:
    mw = o.matrix_world.copy(); o.parent = None; o.data = o.data.copy(); o.data.transform(mw); o.matrix_world = Matrix.Identity(4)
vs = [v.co for o in pecas for v in o.data.vertices]
cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2; cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2; z0 = min(v.z for v in vs)
for o in pecas: o.data.transform(Matrix.Translation((-cx, -cy, -z0)))
for x in bpy.data.objects: x.select_set(False)
for o in pecas: o.select_set(True)
bpy.context.view_layer.objects.active = pecas[0]
dst = os.path.join(OUT, "freezer_horizontal.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[FREEZER] %d pecas: %s, %.0f KB" % (len(pecas), [o.name for o in pecas], os.path.getsize(dst) / 1024))
