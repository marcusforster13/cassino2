"""Cassino clandestino - separa a placa "SOMENTE FUNCIONARIOS" (Placa_Banheiro, dentro de placas.glb) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_placa_funcionarios.py  ->  para_editar/placa_funcionarios.glb
A placa sai como esta na cena (a imagem do autor numa chapa de 80 x 20 cm), centrada na origem e de frente para -Y
(a parede fica do lado +Y). Na cena ela fica na parede do bar, a 2,45 m do chao."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=os.path.join(AQUI, "placas.glb")); bpy.context.view_layer.update()
ob = bpy.data.objects["Placa_Banheiro"]; mw = ob.matrix_world.copy(); ob.parent = None; ob.data.transform(mw); ob.matrix_world.identity()
for o in list(bpy.data.objects):
    if o != ob: bpy.data.objects.remove(o)
vs = [v.co for v in ob.data.vertices]; c = [(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)]
for v in ob.data.vertices: v.co.x -= c[0]; v.co.y -= c[1]; v.co.z -= c[2]
ob.name = "Placa_Somente_Funcionarios"; ob.select_set(True); bpy.context.view_layer.objects.active = ob
dst = os.path.join(OUT, "placa_funcionarios.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[PLACA] %.0f KB" % (os.path.getsize(dst) / 1024))
