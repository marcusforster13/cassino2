"""Cassino clandestino - exporta a lampada simples acesa (o "bulbo" conico) usada no corredor, nos depositos, no quintal
e no beco, para o autor refazer. Uso: blender -b --factory-startup --python exportar_lampada_bulbo.py
-> para_editar/lampada_bulbo.glb. Gera a peca igual a da cena (nao abre o cassino.blend): tronco de cone de 10 cm de
altura, 10 cm de diametro embaixo e 6 cm em cima, aceso (luz quente). Centrado em X e Y; o topo em z = 0 (onde prende no
teto ou no suporte) e a lampada para baixo. A luz de verdade e um ponto de luz a parte, logo abaixo."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=.05, radius2=.03, depth=.1, location=(0, 0, -.05)); o = bpy.context.object; o.name = "Lampada_Bulbo"
m = bpy.data.materials.new("Lampada_Quente"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (1, .9, .75, 1); b.inputs["Emission Color"].default_value = (1, .85, .63, 1); b.inputs["Emission Strength"].default_value = 4
o.data.materials.append(m)
dst = os.path.join(OUT, "lampada_bulbo.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[BULBO] %.0f KB" % (os.path.getsize(dst) / 1024))
