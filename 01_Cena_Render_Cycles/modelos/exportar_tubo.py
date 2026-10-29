"""Cassino clandestino - exporta a lampada tubular do teto (bar e escritorio) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_tubo.py  ->  para_editar/lampada_tubular.glb
Gera a peca igual a da cena (nao abre o cassino.blend): tubo aceso de 1,2 m ao longo de X, 5 cm de largura e 4 cm de
altura, centrado em X e Y, com o topo em z = 0 (encostado no teto; a peca fica pendurada para baixo). Sao 4 na cena
(3 no bar e 1 no escritorio); a luz de verdade e uma lampada a parte, entao a peca pode ter calha, difusor, suportes."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -.02)); o = bpy.context.object; o.name = "Lampada_Tubular"
o.scale = (1.2, .05, .04); bpy.ops.object.transform_apply(scale=True)
m = bpy.data.materials.new("Tubo_Aceso"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (.95, .97, 1, 1); b.inputs["Emission Color"].default_value = (.92, .95, 1, 1); b.inputs["Emission Strength"].default_value = 4
o.data.materials.append(m)
dst = os.path.join(OUT, "lampada_tubular.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[TUBO] %.0f KB" % (os.path.getsize(dst) / 1024))
