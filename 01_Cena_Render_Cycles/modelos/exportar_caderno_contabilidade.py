"""Cassino clandestino - exporta o caderno de contabilidade (mesa do escritorio) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_caderno_contabilidade.py  ->  para_editar/caderno_contabilidade.glb
Gera a peca igual a da cena (nao abre o cassino.blend): capa preta de 21 x 29 cm e 2 cm de espessura, com as folhas
brancas dentro; centrada, base em z = 0, comprimento ao longo de Y. Na cena ele fica deitado na mesa e pode ser recolhido."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
def caixa(nome, tam, pos, cor):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos); o = bpy.context.object; o.name = nome
    o.scale = tam; bpy.ops.object.transform_apply(scale=True)
    m = bpy.data.materials.new(nome); m.diffuse_color = cor; o.data.materials.append(m)
caixa("Caderno_Contabilidade_Capa", (.21, .29, .02), (0, 0, .01), (.02, .02, .02, 1))
caixa("Caderno_Contabilidade_Folhas", (.2, .28, .014), (.003, 0, .013), (.95, .94, .9, 1))
for o in bpy.data.objects: o.select_set(True)
dst = os.path.join(OUT, "caderno_contabilidade.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True)
print("[CADERNO] %.0f KB" % (os.path.getsize(dst) / 1024))
