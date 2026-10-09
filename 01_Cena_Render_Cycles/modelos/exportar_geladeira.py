"""
Cassino clandestino - exporta a geladeira vertical do bar para o autor refazer.

Uso:  blender -b ../cassino.blend --python exportar_geladeira.py      (nao salva a cena)
Saida: modelos/para_editar/geladeira.glb

Sai centrada na origem, com a base no chao (z = 0). Tamanho: 70 cm x 70 cm x 1,90 m. Na cena ela fica encostada na
parede do fundo do balcao, com a porta olhando para -X do Blender.
Para devolver: salve como modelos/geladeira.glb, centrada, base em z = 0 e a porta para -X.
"""
import bpy, os
from mathutils import Matrix

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)

o = bpy.data.objects["Geladeira_Vertical"]
mw = o.matrix_world.copy(); o.parent = None; o.data = o.data.copy(); o.data.transform(mw); o.matrix_world = Matrix.Identity(4)
vs = [v.co for v in o.data.vertices]
cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2; cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2; z0 = min(v.z for v in vs)
o.data.transform(Matrix.Translation((-cx, -cy, -z0)))
for x in bpy.data.objects: x.select_set(False)
o.hide_set(False); o.select_set(True); bpy.context.view_layer.objects.active = o
dst = os.path.join(OUT, "geladeira.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[GELADEIRA] dims %s, %d triangulos, %.0f KB" % ([round(d, 2) for d in o.dimensions], sum(len(p.vertices) - 2 for p in o.data.polygons), os.path.getsize(dst) / 1024))
