"""
Cassino clandestino - exporta UM lustre pendente do salao (o da mesa de carteado) para o autor refazer.

Uso:  blender -b ../cassino.blend --python exportar_lustre.py      (nao salva a cena)
Saida: modelos/para_editar/lustre.glb

O lustre sai centrado na origem em X e Y, na altura real da cena (o fio termina no teto).
Para devolver: salve como modelos/lustre.glb, um lustre so, na mesma posicao.
"""
import bpy, os

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)

base = bpy.data.objects["Pendente_Carteado"]; cx, cy = base.matrix_world.translation.x, base.matrix_world.translation.y
pecas = []
for o in bpy.data.objects:
    if o.type != "MESH" or o.name.startswith(("Teto", "Laje", "Forro")): continue
    p = o.matrix_world.translation
    if abs(p.x - cx) < .35 and abs(p.y - cy) < .35 and p.z > base.matrix_world.translation.z - .3 and max(o.dimensions) < 1.5:
        pecas.append(o)
for o in bpy.data.objects: o.select_set(False)
for o in pecas:
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    o.location.x -= cx; o.location.y -= cy; o.hide_set(False); o.select_set(True)
bpy.context.view_layer.update(); bpy.context.view_layer.objects.active = pecas[0]
dst = os.path.join(OUT, "lustre.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[LUSTRE] %d pecas: %s  (%.0f KB)" % (len(pecas), ", ".join("%s z=%.2f dims=%s" % (o.name, o.location.z, [round(d, 2) for d in o.dimensions]) for o in pecas), os.path.getsize(dst) / 1024))
