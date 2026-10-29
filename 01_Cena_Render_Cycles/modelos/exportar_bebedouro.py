"""Cassino clandestino - exporta o bebedouro do salao de jogos (canto ao lado da porta) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_bebedouro.py  ->  para_editar/bebedouro.glb
Gera a peca igual a da cena (nao abre o cassino.blend): bloco branco de 34 x 34 cm e 1 m de altura, cantos com 2 cm de
chanfro, centrado e com a base em z = 0. Na cena fica no canto, com as paredes atras dele nos lados -Y e +X."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, .5)); o = bpy.context.object; o.name = "Bebedouro"
o.scale = (.34, .34, 1.0); bpy.ops.object.transform_apply(scale=True)
b = o.modifiers.new("chanfro", "BEVEL"); b.width = .02; b.segments = 2
m = bpy.data.materials.new("Plastico_Bebedouro"); m.diffuse_color = (.9, .9, .88, 1); o.data.materials.append(m)
dst = os.path.join(OUT, "bebedouro.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[BEBEDOURO] %.0f KB" % (os.path.getsize(dst) / 1024))
