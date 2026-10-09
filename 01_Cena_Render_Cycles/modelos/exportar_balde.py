"""
Cassino clandestino - exporta UM balde de gelo (o das mesinhas) para o autor refazer.

Uso:  blender -b ../cassino.blend --python exportar_balde.py      (nao salva a cena)
Saida: modelos/para_editar/balde_gelo.glb

O balde sai centrado na origem, com a base no chao (z = 0). Tamanho atual: 16 cm de altura, 20 cm de boca, 16 cm de fundo.
Para devolver: salve como modelos/balde_gelo.glb, um balde so, centrado e com a base em z = 0.
"""
import bpy, os

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)

baldes = sorted([o for o in bpy.data.objects if o.type == "MESH" and "_Balde" in o.name], key=lambda o: o.name)
o = baldes[0]
mw = o.matrix_world.copy(); o.parent = None; o.data.transform(mw); o.matrix_world.identity()
vs = [v.co for v in o.data.vertices]
cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2; cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2; z0 = min(v.z for v in vs)
for v in o.data.vertices: v.co.x -= cx; v.co.y -= cy; v.co.z -= z0
for x in bpy.data.objects: x.select_set(False)
o.hide_set(False); o.select_set(True); bpy.context.view_layer.objects.active = o
dst = os.path.join(OUT, "balde_gelo.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[BALDE] %s, %d baldes na cena (%s), dims %s, %d triangulos, %.0f KB" % (o.name, len(baldes), ", ".join(b.name for b in baldes), [round(d, 3) for d in o.dimensions], sum(len(p.vertices) - 2 for p in o.data.polygons), os.path.getsize(dst) / 1024))
