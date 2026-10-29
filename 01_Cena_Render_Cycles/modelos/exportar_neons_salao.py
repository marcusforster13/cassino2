"""Cassino clandestino - exporta as duas barras de neon do salao (vermelha na parede sul, verde na parede leste) para o
autor refazer. Uso: blender -b --factory-startup --python exportar_neons_salao.py  ->  para_editar/neons_salao.glb
Saem NA POSICAO DA CENA (coordenadas do Blender da cena, piso do salao em z = 0,15): vermelha 2,4 m ao longo de X em
(-0,5; 6,1; 2,65), encostada na parede sul (face em y = 6,075); verde 2,0 m ao longo de Y em (2,4; 7,3; 2,65), encostada
na parede leste (face em x = 2,425). Cada uma tem 4 cm de fundo e 8 cm de altura e acende sozinha (emissao)."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
def barra(nome, tam, pos, cor, emis, forca):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos); o = bpy.context.object; o.name = nome
    o.scale = tam; bpy.ops.object.transform_apply(scale=True)
    m = bpy.data.materials.new(nome + "_Mat"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = cor; b.inputs["Emission Color"].default_value = emis; b.inputs["Emission Strength"].default_value = forca
    o.data.materials.append(m); return o
FZ = .15
a = barra("Neon_Salao_Vermelho", (2.4, .04, .08), (-.5, 6.1, FZ + 2.5), (.25, .03, .04, 1), (1, .16, .16, 1), 6)
b = barra("Neon_Salao_Verde", (.04, 2.0, .08), (2.4, 7.3, FZ + 2.5), (.02, .19, .1, 1), (.16, 1, .48, 1), 5)
for o in (a, b): o.select_set(True)
dst = os.path.join(OUT, "neons_salao.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[NEONS] %.0f KB" % (os.path.getsize(dst) / 1024))
