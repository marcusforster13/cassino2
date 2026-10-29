"""Cassino clandestino - separa o calendario do escritorio (Calendario + Calendario_Faixa, dentro de placas.glb) para o
autor refazer. Uso: blender -b --factory-startup --python exportar_calendario.py  ->  para_editar/calendario.glb
Sai como esta na cena: folha branca de 34 x 50 cm com a faixa vermelha em cima, centrada na origem e de frente para +Y
(a parede fica do lado -Y). Na cena fica na parede do escritorio, com o centro a 1,75 m do chao."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=os.path.join(AQUI, "placas.glb")); bpy.context.view_layer.update()
obs = [bpy.data.objects[n] for n in ("Calendario", "Calendario_Faixa")]
for ob in obs: mw = ob.matrix_world.copy(); ob.parent = None; ob.data.transform(mw); ob.matrix_world.identity()
for o in list(bpy.data.objects):
    if o not in obs: bpy.data.objects.remove(o)
vs = [v.co.copy() for ob in obs for v in ob.data.vertices]; c = [(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)]
for ob in obs:
    for v in ob.data.vertices: v.co.x -= c[0]; v.co.y -= c[1]; v.co.z -= c[2]
    ob.select_set(True)
bpy.context.view_layer.objects.active = obs[0]
dst = os.path.join(OUT, "calendario.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[CALENDARIO] %.0f KB" % (os.path.getsize(dst) / 1024))
