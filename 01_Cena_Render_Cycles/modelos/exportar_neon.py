"""Cassino clandestino - separa o neon "CERVEJA GELADA" da fachada (Bar_Neon_Cerveja, dentro de placas.glb) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_neon.py  ->  para_editar/neon_cerveja_gelada.glb
Sai como esta na cena: letras finas de neon ambar com 1,58 m de largura e 18 cm de altura, centradas na origem e de
frente para -Y (a rua). Na cena ficam na fachada, acima da porta de enrolar, a 3,1 m do chao."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=os.path.join(AQUI, "placas.glb")); bpy.context.view_layer.update()
obs = [bpy.data.objects[n] for n in ("Bar_Neon_Cerveja",)]
for ob in obs: mw = ob.matrix_world.copy(); ob.parent = None; ob.data.transform(mw); ob.matrix_world.identity()
for o in list(bpy.data.objects):
    if o not in obs: bpy.data.objects.remove(o)
vs = [v.co.copy() for ob in obs for v in ob.data.vertices]; c = [(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)]
for ob in obs:
    for v in ob.data.vertices: v.co.x -= c[0]; v.co.y -= c[1]; v.co.z -= c[2]
    ob.select_set(True)
bpy.context.view_layer.objects.active = obs[0]
dst = os.path.join(OUT, "neon_cerveja_gelada.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[NEON] %.0f KB" % (os.path.getsize(dst) / 1024))
