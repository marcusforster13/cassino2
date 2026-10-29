"""Cassino clandestino - exporta a banqueta do balcao (Poly Haven bar_chair_round_01, ja reduzida como na cena) para o
autor refazer. Uso: blender -b ../cassino.blend --python exportar_banqueta.py  ->  para_editar/banqueta.glb
Sai uma copia, sem o giro da cena, centrada em XY e com a base no chao (z = 0). A mesma malha e usada no bar e na sala reservada."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
copias = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("Banqueta_Bar", "Banqueta_Sala"))]
ob = next(o for o in copias if o.name.startswith("Banqueta_Bar"))
for o in bpy.data.objects: o.select_set(False)
ob.parent = None; ob.location = (0, 0, 0); ob.rotation_euler = (0, 0, 0); ob.hide_set(False); ob.select_set(True)
bpy.context.view_layer.objects.active = ob; bpy.context.view_layer.update()
tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
dst = os.path.join(OUT, "banqueta.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[BANQUETA] %d triangulos, %d copias na cena (%s), %.0f KB" % (tris, len(copias), sorted({o.data.name for o in copias}), os.path.getsize(dst) / 1024))
