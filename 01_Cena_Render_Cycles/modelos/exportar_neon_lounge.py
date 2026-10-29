"""Cassino clandestino - exporta o letreiro de neon LOUNGE da sala reservada para o autor refazer.
Uso: blender -b ../cassino.blend --python exportar_neon_lounge.py  ->  para_editar/neon_lounge.glb
Sai NA POSICAO DA CENA (coordenadas do Blender da cena, piso em z = 0,15): letras de 34 cm de altura, centradas em
(9,6; 6,14; 2,35), na parede sul da sala (revestimento em y = 6,115) e de frente para +Y (para dentro da sala)."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("Sala_Neon_Lounge",))]
for o in bpy.data.objects: o.select_set(False)
for o in objs: o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
dst = os.path.join(OUT, "neon_lounge.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[LOUNGE] %d pecas (%s), %.0f KB" % (len(objs), ", ".join(sorted({o.name.split(".")[0] for o in objs})), os.path.getsize(dst) / 1024))
