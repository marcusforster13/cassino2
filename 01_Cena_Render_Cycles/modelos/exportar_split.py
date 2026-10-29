"""Cassino clandestino - exporta o ar-condicionado split do salao (unidade de dentro, na parede ao lado do neon) para o
autor refazer. Uso: blender -b --factory-startup --python exportar_split.py  ->  para_editar/ar_split.glb
Gera a peca igual a da cena (nao abre o cassino.blend): bloco branco de 90 cm de largura, 22 cm de fundo e 28 cm de
altura, cantos com 3 cm de chanfro. Centrado em X e Z na origem; a parede fica do lado -Y (y = 0 e a face da parede) e a
frente para +Y. Na cena fica a 2,55 m do chao (centro), com o conduite do teto chegando por cima."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, .11, 0)); o = bpy.context.object; o.name = "Ar_Split"
o.scale = (.9, .22, .28); bpy.ops.object.transform_apply(scale=True)
b = o.modifiers.new("chanfro", "BEVEL"); b.width = .03; b.segments = 3
m = bpy.data.materials.new("Plastico_Branco_Split"); m.diffuse_color = (.9, .9, .88, 1); o.data.materials.append(m)
dst = os.path.join(OUT, "ar_split.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[SPLIT] %.0f KB" % (os.path.getsize(dst) / 1024))
