"""Cassino clandestino - exporta o bar da sala reservada (balcao com tampo rosa, fita de LED embaixo e as duas prateleiras de
garrafas com LED) para o autor refazer. Uso: blender -b ../cassino.blend --python exportar_bar_sala.py  ->  para_editar/bar_sala_reservada.glb
Sai NA POSICAO DA CENA (coordenadas do Blender da cena, piso em z = 0,15): balcao de 0,5 x 2,3 m e 1,05 m de altura em
x = 7,15 (atendente do lado -X), prateleiras na parede oeste (x = 6,24). As garrafas ficam a parte (modelo garrafa.glb)."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("Bar_Sala_",))]
for o in bpy.data.objects: o.select_set(False)
for o in objs: o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
dst = os.path.join(OUT, "bar_sala_reservada.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[BAR_SALA] %d pecas (%s), %.0f KB" % (len(objs), ", ".join(sorted({o.name.split(".")[0] for o in objs})), os.path.getsize(dst) / 1024))
