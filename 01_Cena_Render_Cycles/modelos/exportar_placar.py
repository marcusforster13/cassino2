"""
Cassino clandestino - exporta a placa "ACUMULADO" do salao de jogos para o autor refazer.

Uso:  blender -b ../cassino.blend --python exportar_placar.py      (nao salva a cena)
Saida: modelos/para_editar/placar_acumulado.glb

A placa sai centrada na origem, de frente para -Y do Blender (o texto olha para -Y), no tamanho real: 2,60 m x 0,42 m.
Para devolver: salve como modelos/placar_acumulado.glb, na mesma posicao e de frente para -Y.
"""
import bpy, os

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)

pecas = []
for o in bpy.data.objects:
    if o.type not in ("MESH", "FONT", "CURVE"): continue
    p = o.matrix_world.translation
    if o.name.startswith("Placar_Acumulado") or (abs(p.x + 1.3) < 1.4 and abs(p.y - 12.76) < .06 and 2.2 < p.z - 0 < 3.2 and max(o.dimensions) < 2.8 and "Cortina" not in o.name):
        pecas.append(o)
ref = next((o for o in pecas if o.name == "Placar_Acumulado"), pecas[0]); c = ref.matrix_world.translation.copy()
for o in bpy.data.objects: o.select_set(False)
for o in pecas:
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    o.location -= c; o.hide_set(False); o.select_set(True)
bpy.context.view_layer.update(); bpy.context.view_layer.objects.active = pecas[0]
dst = os.path.join(OUT, "placar_acumulado.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[PLACAR] %d pecas: %s  (%.0f KB)" % (len(pecas), ", ".join("%s %s dims=%s" % (o.name, o.type, [round(d, 2) for d in o.dimensions]) for o in pecas), os.path.getsize(dst) / 1024))
