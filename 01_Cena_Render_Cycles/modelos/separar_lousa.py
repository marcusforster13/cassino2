"""Cassino clandestino - separa a lousa do cardapio da calcada (objeto Plane de placas.glb, a imagem do autor) em
modelos/cardapio_lousa.glb, para a cena a encostar inclinada na fachada. Uso: blender -b --factory-startup --python separar_lousa.py"""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = AQUI
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=os.path.join(AQUI, "placas.glb")); bpy.context.view_layer.update()
obs = [bpy.data.objects[n] for n in ("Plane",)]
for ob in obs: mw = ob.matrix_world.copy(); ob.parent = None; ob.data.transform(mw); ob.matrix_world.identity()
for o in list(bpy.data.objects):
    if o not in obs: bpy.data.objects.remove(o)
vs = [v.co.copy() for ob in obs for v in ob.data.vertices]; c = [(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)]
for ob in obs:
    for v in ob.data.vertices: v.co.x -= c[0]; v.co.y -= c[1]; v.co.z -= c[2]
    ob.select_set(True)
bpy.context.view_layer.objects.active = obs[0]
dst = os.path.join(OUT, "cardapio_lousa.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[LOUSA] %.0f KB" % (os.path.getsize(dst) / 1024))
