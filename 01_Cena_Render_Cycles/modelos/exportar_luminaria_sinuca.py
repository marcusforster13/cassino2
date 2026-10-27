"""Cassino clandestino - exporta a luminaria da mesa de sinuca (bar) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_luminaria_sinuca.py  ->  para_editar/luminaria_sinuca.glb
Gera a peca igual a da cena (nao abre o cassino.blend): corpo verde de 1,20 m (X) x 30 cm (Y) x 10 cm, a placa de luz
embaixo e os dois fios ate o teto (1 m de fio, a cena corta no teto). O fundo do corpo fica em z = 0."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
def peca(nome, op, tam, pos, cor, **kw):
    op(location=pos, **kw); o = bpy.context.object; o.name = nome; o.scale = tam; bpy.ops.object.transform_apply(scale=True)
    m = bpy.data.materials.new(nome); m.diffuse_color = cor; o.data.materials.append(m); return o
o = peca("Luminaria_Corpo", bpy.ops.mesh.primitive_cube_add, (1.2, .3, .1), (0, 0, .05), (.05, .5, .15, 1), size=1)
b = o.modifiers.new("chanfro", "BEVEL"); b.width = .02; b.segments = 2
peca("Luminaria_Luz", bpy.ops.mesh.primitive_cube_add, (1.1, .2, .02), (0, 0, -.005), (1, .9, .7, 1), size=1)
for sx in (-.5, .5): peca("Luminaria_Fio", bpy.ops.mesh.primitive_cylinder_add, (.006, .006, .5), (sx, 0, .6), (.02, .02, .02, 1), vertices=6)
for o in bpy.data.objects: o.select_set(True)
dst = os.path.join(OUT, "luminaria_sinuca.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[LUMINARIA] %.0f KB" % (os.path.getsize(dst) / 1024))
