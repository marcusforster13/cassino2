"""
Cassino clandestino - grava um .blend so com as pecas que o autor vai melhorar.

Uso:  blender -b ../cassino.blend --python exportar_blend_para_editar.py
Saida: modelos/para_editar/pecas_para_editar.blend  (texturas embutidas; a cena original nao e alterada)

Conteudo: bolas e mesa de sinuca, relogio de parede e UMA cadeira de plastico (todas as cadeiras da cena usam a
mesma malha). As pecas ficam na posicao em que estao na cena: nao mova, so melhore forma, material e textura.
Para devolver: exporte em .glb com os mesmos nomes de objeto (ou mande o proprio .blend).
"""
import bpy, os

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)
MANTER = ("Sinuca_", "Relogio_")
cadeira = next((o for o in bpy.data.objects if o.name.startswith("Cadeira_Bar_")), None)
manter = {o for o in bpy.data.objects if o.name.startswith(MANTER) and o.type == "MESH"}
if cadeira:
    cadeira.name = "Cadeira_Plastico_Modelo"; cadeira.data = cadeira.data.copy(); cadeira.data.name = "Cadeira_Plastico"; manter.add(cadeira)
for o in list(bpy.data.objects):
    if o not in manter: bpy.data.objects.remove(o, do_unlink=True)
col = bpy.data.collections.new("Pecas_para_editar"); bpy.context.scene.collection.children.link(col)
for o in manter:
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
for c in [c for c in bpy.data.collections if c is not col]: bpy.data.collections.remove(c)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
# luz e camera simples para ver as pecas ao abrir
sol = bpy.data.objects.new("Luz", bpy.data.lights.new("Luz", "SUN")); sol.data.energy = 3; sol.rotation_euler = (.7, .2, .6); col.objects.link(sol)
bpy.context.scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
bpy.context.scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.5, .5, .5, 1)
try: bpy.ops.file.pack_all()
except Exception as e: print("[BLEND] aviso ao embutir texturas:", e)
dst = os.path.join(OUT, "pecas_para_editar.blend")
bpy.ops.wm.save_as_mainfile(filepath=dst, copy=True)
print("[BLEND] %s: %d pecas (%s), %.1f MB" % (os.path.basename(dst), len(manter), ", ".join(sorted({o.name.split('.')[0] for o in manter})), os.path.getsize(dst) / 1e6))
