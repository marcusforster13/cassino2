"""Cassino clandestino - exporta o varal do quintal (o fio e as 4 pecas de roupa penduradas) para o autor refazer.
Uso: blender -b ../cassino.blend --python exportar_varal.py  ->  para_editar/varal_roupas.glb
Sai NA POSICAO DA CENA (coordenadas do Blender da cena, piso em z = 0,15): fio de 11,6 m ao longo de X em y = 16,6, a
1,9 m do chao (junto do muro dos fundos); roupas de 50 x 45 cm penduradas a partir de x = -3,5, a cada 90 cm."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("Varal", "Pano_Varal"))]
for o in bpy.data.objects: o.select_set(False)
for o in objs: o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
dst = os.path.join(OUT, "varal_roupas.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[VARAL] %d pecas (%s), %.0f KB" % (len(objs), ", ".join(sorted({o.name.split(".")[0] for o in objs})), os.path.getsize(dst) / 1024))
