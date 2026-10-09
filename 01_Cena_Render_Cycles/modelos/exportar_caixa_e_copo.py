"""
Cassino clandestino - exporta a caixa registradora do bar e UM copo para o autor refazer.

Uso:  blender -b ../cassino.blend --python exportar_caixa_e_copo.py      (nao salva a cena)
Saida: modelos/para_editar/caixa_registradora.glb  e  modelos/para_editar/copo.glb

As duas pecas saem centradas na origem, com a base no chao (z = 0).
- Caixa registradora: 34 cm (X) x 38 cm (Y) x 20 cm de altura; o visor olha para -X (lado do cliente).
- Copo: 10 cm de altura, 6 cm de boca. Na cena ha copos de 9 e de 10 cm (balcao, mesas do bar, mesa de carteado, mesinhas).
Para devolver: salve como modelos/caixa_registradora.glb e modelos/copo.glb, centradas e com a base em z = 0.
"""
import bpy, os
from mathutils import Matrix

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)

def exportar(pecas, arq):
    for o in pecas:
        mw = o.matrix_world.copy(); o.parent = None; o.data = o.data.copy(); o.data.transform(mw); o.matrix_world = Matrix.Identity(4)
    vs = [v.co for o in pecas for v in o.data.vertices]
    cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2; cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2; z0 = min(v.z for v in vs)
    for o in pecas: o.data.transform(Matrix.Translation((-cx, -cy, -z0)))
    for x in bpy.data.objects: x.select_set(False)
    for o in pecas: o.hide_set(False); o.select_set(True)
    bpy.context.view_layer.objects.active = pecas[0]
    dst = os.path.join(OUT, arq)
    bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
    vs = [v.co for o in pecas for v in o.data.vertices]
    print("[EXPORTA] %s: %d pecas (%s), %d triangulos, dims %s, %.0f KB" % (arq, len(pecas), ", ".join(o.name for o in pecas), sum(len(p.vertices) - 2 for o in pecas for p in o.data.polygons),
          [round(max(v[i] for v in vs) - min(v[i] for v in vs), 3) for i in range(3)], os.path.getsize(dst) / 1024))

exportar([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Caixa_Registradora")], "caixa_registradora.glb")
copos = sorted([o for o in bpy.data.objects if o.type == "MESH" and "Copo" in o.name], key=lambda o: o.name)
print("[EXPORTA] copos na cena: %d (%s)" % (len(copos), ", ".join(o.name for o in copos)))
exportar([next(o for o in copos if o.name.startswith("Copo_Balcao"))], "copo.glb")
