"""Cassino clandestino - exporta as 9 pastas de arquivo (as "livros" coloridos) e a prateleira do escritorio para o autor refazer.
Uso: blender -b ../cassino.blend --python exportar_pastas.py  ->  para_editar/pastas_prateleira.glb
Sai NA POSICAO DA CENA (coordenadas do Blender da cena, piso em z = 0,15): prateleira de 28 cm x 1,6 m na parede leste do
escritorio (x = 5,76), a 1,6 m do chao; as pastas de 24 x 7 x 30 cm em pe sobre ela, com a lombada para -X (o escritorio; a parede fica em +X)."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("Pasta_Arquivo", "Prateleira_Escritorio"))]
for o in bpy.data.objects: o.select_set(False)
for o in objs: o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
dst = os.path.join(OUT, "pastas_prateleira.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[PASTAS] %d pecas (%s), %.0f KB" % (len(objs), ", ".join(sorted({o.name.split(".")[0] for o in objs})), os.path.getsize(dst) / 1024))
