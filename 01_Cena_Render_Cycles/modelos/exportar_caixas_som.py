"""Cassino clandestino - exporta as duas caixas de som do palco da sala reservada (uma de cada lado) para o autor refazer.
Uso: blender -b ../cassino.blend --python exportar_caixas_som.py  ->  para_editar/caixas_som.glb
Sai NA POSICAO DA CENA (coordenadas do Blender da cena, piso em z = 0,15): caixas de 38 x 34 x 70 cm com dois falantes,
nos cantos do fundo da sala (x = 6,65 e 11,35; y = 12,55), com os falantes virados para -Y (a sala)."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("Caixa_Som",))]
for o in bpy.data.objects: o.select_set(False)
for o in objs: o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
dst = os.path.join(OUT, "caixas_som.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[CAIXAS] %d pecas (%s), %.0f KB" % (len(objs), ", ".join(sorted({o.name.split(".")[0] for o in objs})), os.path.getsize(dst) / 1024))
