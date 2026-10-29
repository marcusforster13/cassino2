"""Cassino clandestino - exporta a mesinha redonda preta (salao e sala reservada; em cima ficam garrafa, copos e balde)
para o autor refazer. Uso: blender -b --factory-startup --python exportar_mesinha.py  ->  para_editar/mesinha.glb
Gera a peca igual a da cena (nao abre o cassino.blend): pe conico de metal (16 cm embaixo, 4 cm em cima, 44 cm de altura)
e tampo preto de 64 cm de diametro e 3 cm de espessura, com o topo a 47 cm. Centrada em X e Y, base no chao (z = 0).
Garrafa, copos e balde ficam a parte: se o tampo mudar de altura, me avise para acertar a altura deles."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=.16, radius2=.04, depth=.44, location=(0, 0, .22)); pe = bpy.context.object; pe.name = "Mesinha_Pe"
bpy.ops.mesh.primitive_cylinder_add(vertices=22, radius=.32, depth=.03, location=(0, 0, .455)); tp = bpy.context.object; tp.name = "Mesinha_Tampo"
m1 = bpy.data.materials.new("Metal_Pe"); m1.diffuse_color = (.35, .36, .38, 1); m1.metallic = 1; pe.data.materials.append(m1)
m2 = bpy.data.materials.new("Preto_Brilhante"); m2.diffuse_color = (.02, .02, .02, 1); m2.roughness = .2; tp.data.materials.append(m2)
for o in (pe, tp): o.select_set(True)
dst = os.path.join(OUT, "mesinha.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[MESINHA] %.0f KB" % (os.path.getsize(dst) / 1024))
