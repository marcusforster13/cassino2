"""Cassino clandestino - exporta o interruptor de parede (placa branca com a tecla; a cena tem interruptores a 1,15 m do chao, ao lado das portas;
as tomadas usam a mesma placa) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_interruptor.py  ->  para_editar/interruptor.glb
Gera a peca igual a da cena (nao abre o cassino.blend): placa de 7,5 x 11,5 cm e 1,2 cm de espessura, tecla de 3 x 5 cm.
Centrada em X e Z na origem; a parede fica do lado -Y (y = 0 e a face da parede) e a frente para +Y."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
def caixa(nome, tam, pos, cor, chanfro=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos); o = bpy.context.object; o.name = nome
    o.scale = tam; bpy.ops.object.transform_apply(scale=True)
    if chanfro: b = o.modifiers.new("chanfro", "BEVEL"); b.width = chanfro; b.segments = 2
    m = bpy.data.materials.new(nome + "_Mat"); m.diffuse_color = cor; o.data.materials.append(m); return o
a = caixa("Interruptor_Placa", (.075, .012, .115), (0, .006, 0), (.85, .84, .8, 1), .004)
b = caixa("Interruptor_Tecla", (.03, .006, .05), (0, .014, 0), (.8, .79, .76, 1))
for o in (a, b): o.select_set(True)
dst = os.path.join(OUT, "interruptor.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[INTERRUPTOR] %.0f KB" % (os.path.getsize(dst) / 1024))
