"""Cassino clandestino - exporta a macaneta das portas (salao, escritorio e fundos) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_macaneta.py  ->  para_editar/macaneta.glb
Gera a peca igual a da cena (nao abre o cassino.blend): cilindro de 5 cm de diametro e 5 cm de comprimento, deitado
no eixo Y. A folha da porta fica do lado -Y (base da peca em y = 0) e a ponta da macaneta para +Y; centro em x = z = 0.
A cena usa a mesma peca dos dois lados de cada porta, a 1,02 m do chao e 9 cm da borda da folha."""
import bpy, os, math
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=.025, depth=.05, location=(0, .025, 0), rotation=(math.pi / 2, 0, 0))
o = bpy.context.object; o.name = "Macaneta"; bpy.ops.object.transform_apply(location=False, rotation=True)
m = bpy.data.materials.new("Metal_Macaneta"); m.diffuse_color = (.6, .6, .62, 1); m.metallic = 1; o.data.materials.append(m)
dst = os.path.join(OUT, "macaneta.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[MACANETA] %.0f KB" % (os.path.getsize(dst) / 1024))
