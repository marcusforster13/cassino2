"""Cassino clandestino - exporta a cadeira de visita do escritorio (branca, de frente para a mesa) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_cadeira_visita.py  ->  para_editar/cadeira_visita.glb
Gera a peca igual a da cena (nao abre o cassino.blend): assento de 44 x 44 cm a 45 cm do chao, encosto de 42 cm e quatro
pes finos. Centrada em X e Y, base no chao (z = 0); o encosto fica do lado -Y e quem senta olha para +Y."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
m = bpy.data.materials.new("Branco_Cadeira"); m.diffuse_color = (.85, .85, .83, 1)
pecas = []
def caixa(nome, tam, pos, chanfro):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos); o = bpy.context.object; o.name = nome
    o.scale = tam; bpy.ops.object.transform_apply(scale=True)
    b = o.modifiers.new("chanfro", "BEVEL"); b.width = chanfro; b.segments = 2; o.data.materials.append(m); pecas.append(o)
caixa("Cadeira_Visita_Assento", (.44, .44, .06), (0, 0, .45), .015)
caixa("Cadeira_Visita_Encosto", (.42, .04, .42), (0, -.21, .72), .012)
for sx in (-1, 1):
    for sy in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=.017, depth=.44, location=(sx * .19, sy * .19, .22))
        o = bpy.context.object; o.name = "Cadeira_Visita_Pe"; o.data.materials.append(m); pecas.append(o)
for o in pecas: o.select_set(True)
dst = os.path.join(OUT, "cadeira_visita.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[CADEIRA] %.0f KB" % (os.path.getsize(dst) / 1024))
