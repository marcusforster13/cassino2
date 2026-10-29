"""Cassino clandestino - exporta a lixeira do salao (canto, perto da porta do corredor) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_lixeira.py  ->  para_editar/lixeira.glb
Gera a peca igual a da cena (nao abre o cassino.blend): cilindro de plastico preto, 32 cm de diametro na boca e 26 cm na
base, 42 cm de altura, centrado em X e Y e com a base no chao (z = 0)."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_cone_add(vertices=14, radius1=.13, radius2=.16, depth=.42, location=(0, 0, .21)); o = bpy.context.object; o.name = "Lixeira"
m = bpy.data.materials.new("Plastico_Lixeira"); m.diffuse_color = (.03, .03, .03, 1); m.roughness = .5; o.data.materials.append(m)
dst = os.path.join(OUT, "lixeira.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[LIXEIRA] %.0f KB" % (os.path.getsize(dst) / 1024))
