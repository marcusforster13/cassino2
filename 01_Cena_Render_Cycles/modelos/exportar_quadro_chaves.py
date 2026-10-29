"""Cassino clandestino - separa o quadro de chaves do escritorio (Quadro_Chaves, dentro de placas.glb) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_quadro_chaves.py  ->  para_editar/quadro_chaves.glb
Sai como esta na cena: tabua de madeira de 50 x 40 cm e as 6 chaves douradas, centrada na origem e de frente para +Y (a parede
fica do lado -Y). Na cena fica na parede do escritorio, com o centro a 1,55 m do chao."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=os.path.join(AQUI, "placas.glb")); bpy.context.view_layer.update()
obs = [bpy.data.objects[n] for n in ("Quadro_Chaves",)]
for ob in obs: mw = ob.matrix_world.copy(); ob.parent = None; ob.data.transform(mw); ob.matrix_world.identity()
for o in list(bpy.data.objects):
    if o not in obs: bpy.data.objects.remove(o)
vs = [v.co.copy() for ob in obs for v in ob.data.vertices]; c = [(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)]
for ob in obs:
    for v in ob.data.vertices: v.co.x -= c[0]; v.co.y -= c[1]; v.co.z -= c[2]
    ob.select_set(True)
m = bpy.data.materials.new("Chave_Dourada"); m.diffuse_color = (.75, .52, .15, 1); m.metallic = 1; m.roughness = .35
for k in range(6):                                          # as 6 chaves penduradas (na cena sao pecas a parte, na frente da tabua)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-.18 + k * .072, .015, 0)); c = bpy.context.object; c.name = "Chave_Pendurada"
    c.scale = (.02, .01, .07); bpy.ops.object.transform_apply(scale=True); c.data.materials.append(m); c.select_set(True)
for o in obs: o.select_set(True)                       # criar as chaves tira a selecao da tabua
for o in bpy.data.objects:
    if o.name.startswith("Chave_Pendurada"): o.select_set(True)
bpy.context.view_layer.objects.active = obs[0]
dst = os.path.join(OUT, "quadro_chaves.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[CHAVES] %.0f KB" % (os.path.getsize(dst) / 1024))
