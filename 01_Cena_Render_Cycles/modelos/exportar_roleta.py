"""
Cassino clandestino - exporta a mesa de roleta do salao (mesa, feltro, bacia, disco, eixo, casas e quadro de apostas)
para o autor refazer.

Uso:  blender -b ../cassino.blend --python exportar_roleta.py      (nao salva a cena)
Saida: modelos/para_editar/roleta.glb

As pecas saem NA POSICAO DA CENA (nao centralizadas): e so editar e salvar no mesmo lugar.
Para devolver: salve como modelos/roleta.glb, sem mover o conjunto.
"""
import bpy, os

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)

pecas = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("Mesa_Roleta_", "Roleta_"))]
for o in bpy.data.objects: o.select_set(False)
for o in pecas: o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = pecas[0]
dst = os.path.join(OUT, "roleta.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
dg = bpy.context.evaluated_depsgraph_get(); tris = 0
for o in pecas:
    e = o.evaluated_get(dg); m = e.to_mesh(); tris += sum(len(p.vertices) - 2 for p in m.polygons); e.to_mesh_clear()
nomes = sorted({o.name.split(".")[0] for o in pecas})
print("[ROLETA] %d pecas, %d triangulos, %.0f KB: %s" % (len(pecas), tris, os.path.getsize(dst) / 1024, ", ".join(nomes)))
