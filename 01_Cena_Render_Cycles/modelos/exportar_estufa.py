"""Cassino clandestino - exporta a estufa de salgados do balcao (base, vidro e luz) para o autor refazer.
Uso: blender -b ../cassino.blend --python exportar_estufa.py  ->  para_editar/estufa_salgados.glb
Sai centrada, base em z = 0, na orientacao da cena: comprida em Y (80 cm), 46 cm de largura em X, 36 cm de altura;
o atendente fica do lado +X e o cliente do lado -X. Os salgados nao vao junto (ficam como estao)."""
import bpy, os
from mathutils import Matrix
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
pecas = [o for o in bpy.data.objects if o.type == "MESH" and o.name.split(".")[0] in ("Estufa_Base", "Estufa_Vidro", "Estufa_Luz")]
for o in pecas:
    mw = o.matrix_world.copy(); o.parent = None; o.data = o.data.copy(); o.data.transform(mw); o.matrix_world = Matrix.Identity(4)
vs = [v.co for o in pecas for v in o.data.vertices]
cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2; cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2; z0 = min(v.z for v in vs)
for o in pecas: o.data.transform(Matrix.Translation((-cx, -cy, -z0)))
for x in bpy.data.objects: x.select_set(False)
for o in pecas: o.select_set(True)
bpy.context.view_layer.objects.active = pecas[0]
dst = os.path.join(OUT, "estufa_salgados.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[ESTUFA] %d pecas: %s, %.0f KB" % (len(pecas), [o.name for o in pecas], os.path.getsize(dst) / 1024))
