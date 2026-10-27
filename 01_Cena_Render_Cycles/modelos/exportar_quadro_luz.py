"""Cassino clandestino - exporta o quadro de luz (caixa de disjuntores na parede do salao) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_quadro_luz.py  ->  para_editar/quadro_de_luz.glb
Gera a peca igual a da cena (nao abre o cassino.blend): 40 cm de largura (X), 10 cm de fundo (Y) e 55 cm de altura,
cantos com 1 cm de chanfro, centrada e com a base em z = 0. A parede fica do lado -Y e a porta do quadro para +Y."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, .275)); o = bpy.context.object; o.name = "Quadro_de_Luz"
o.scale = (.4, .1, .55); bpy.ops.object.transform_apply(scale=True)
b = o.modifiers.new("chanfro", "BEVEL"); b.width = .01; b.segments = 2
m = bpy.data.materials.new("Metal_Quadro"); m.diffuse_color = (.35, .36, .38, 1); o.data.materials.append(m)
dst = os.path.join(OUT, "quadro_de_luz.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[QUADRO] %.0f KB" % (os.path.getsize(dst) / 1024))
