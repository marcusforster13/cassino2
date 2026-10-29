"""Cassino clandestino - separa a placa ALUGA-SE da loja fechada (Loja_Fechada_Aluga, dentro de placas.glb) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_aluga_se.py  ->  para_editar/placa_aluga_se.glb
Sai como esta na cena: chapa de 1,20 x 0,50 m com a imagem do autor, centrada na origem e de frente para -Y (a rua);
a porta de aco fica atras (+Y). Na cena fica pendurada na porta da loja, com o centro a 1,9 m da calcada."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=os.path.join(AQUI, "placas.glb")); bpy.context.view_layer.update()
obs = [bpy.data.objects[n] for n in ("Loja_Fechada_Aluga",)]
for ob in obs: mw = ob.matrix_world.copy(); ob.parent = None; ob.data.transform(mw); ob.matrix_world.identity()
for o in list(bpy.data.objects):
    if o not in obs: bpy.data.objects.remove(o)
vs = [v.co.copy() for ob in obs for v in ob.data.vertices]; c = [(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)]
for ob in obs:
    for v in ob.data.vertices: v.co.x -= c[0]; v.co.y -= c[1]; v.co.z -= c[2]
    ob.select_set(True)
bpy.context.view_layer.objects.active = obs[0]
dst = os.path.join(OUT, "placa_aluga_se.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[ALUGA] %.0f KB" % (os.path.getsize(dst) / 1024))
