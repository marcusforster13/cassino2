"""Cassino clandestino - exporta o pendente verde (luminaria das mesas de carteado e da roleta, no salao) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_pendente.py  ->  para_editar/pendente.glb
Gera a peca igual a da cena (nao abre o cassino.blend): cupula conica de 60 cm de diametro e 24 cm de altura, aberta
embaixo, e o fio ate o teto (68 cm). A borda de baixo da cupula fica em z = 0. Na cena sao dois iguais."""
import bpy, os, bmesh, math
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
perfil = [(.04, .22), (.28, 0), (.3, 0), (.06, .24)]; seg = 20
me = bpy.data.meshes.new("Pendente"); bm = bmesh.new()
aneis = [[bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z)) for k in range(seg)] for r, z in perfil]
for a, b in zip(aneis, aneis[1:]):
    for k in range(seg): bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
bm.normal_update(); bm.to_mesh(me); bm.free()
o = bpy.data.objects.new("Pendente_Cupula", me); bpy.context.collection.objects.link(o)
m = bpy.data.materials.new("Metal_Verde"); m.diffuse_color = (.03, .4, .12, 1); me.materials.append(m)
bpy.ops.mesh.primitive_cylinder_add(radius=.006, depth=.68, vertices=6, location=(0, 0, .22 + .34)); f = bpy.context.object; f.name = "Pendente_Fio"
mf = bpy.data.materials.new("Fio_Preto"); mf.diffuse_color = (.02, .02, .02, 1); f.data.materials.append(mf)
for x in bpy.data.objects: x.select_set(True)
dst = os.path.join(OUT, "pendente.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True)
print("[PENDENTE] %.0f KB" % (os.path.getsize(dst) / 1024))
