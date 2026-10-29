"""Cassino clandestino - exporta o palco da sala reservada (tablado, degraus, fitas de LED, as duas barras de pole dance e
o espelho do fundo) para o autor refazer. Uso: blender -b ../cassino.blend --python exportar_palco.py
-> para_editar/palco.glb. Sai NA POSICAO DA CENA (coordenadas do Blender da cena, piso em z = 0,15): tablado de
3,8 x 1,9 m e 35 cm de altura centrado em (9; 11,9), frente para -Y (o salao da sala), espelho na parede do fundo (y 12,86)."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("Palco", "Pole_Dance"))]
for o in bpy.data.objects: o.select_set(False)
for o in objs: o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
dst = os.path.join(OUT, "palco.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[PALCO] %d pecas (%s), %.0f KB" % (len(objs), ", ".join(sorted({o.name.split(".")[0] for o in objs})), os.path.getsize(dst) / 1024))
