"""Cassino clandestino - exporta o globo espelhado da sala reservada para o autor refazer.
Uso: blender -b --factory-startup --python exportar_globo.py  ->  para_editar/globo_espelhado.glb
Gera a peca igual a da cena (nao abre o cassino.blend): esfera facetada de 34 cm de diametro com a haste de 16 cm que a
prende no forro. O topo da haste (o ponto preso no teto) fica em z = 0 e o globo pendurado abaixo, centrado em X e Y."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=.17, location=(0, 0, -.31)); g = bpy.context.object; g.name = "Globo_Espelhado"
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=.008, depth=.16, location=(0, 0, -.08)); h = bpy.context.object; h.name = "Globo_Espelhado_Haste"
m = bpy.data.materials.new("Cromo_Globo"); m.diffuse_color = (.85, .85, .9, 1); m.metallic = 1; m.roughness = .1; g.data.materials.append(m)
m2 = bpy.data.materials.new("Metal_Haste"); m2.diffuse_color = (.1, .1, .1, 1); h.data.materials.append(m2)
for o in (g, h): o.select_set(True)
dst = os.path.join(OUT, "globo_espelhado.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[GLOBO] %.0f KB" % (os.path.getsize(dst) / 1024))
