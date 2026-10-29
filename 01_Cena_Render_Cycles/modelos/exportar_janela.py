"""Cassino clandestino - exporta a janela do sobrado (fachada, segundo andar) para o autor refazer.
Uso: blender -b --factory-startup --python exportar_janela.py  ->  para_editar/janela_sobrado.glb
Gera a peca igual a da cena (nao abre o cassino.blend): moldura preta de 1,54 x 1,44 m (10 cm de fundo) e o vidro de
1,40 x 1,30 m na frente. Centrada em X e Z na origem, de frente para -Y (a rua); a parede fica do lado +Y (y = 0 e a face
da fachada). Sao 4 na cena, a 5,1 m do chao: tres apagadas (vidro escuro) e uma com cortina bege acesa (a da foto)."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
def caixa(nome, tam, pos, cor):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos); o = bpy.context.object; o.name = nome
    o.scale = tam; bpy.ops.object.transform_apply(scale=True)
    m = bpy.data.materials.new(nome + "_Mat"); m.diffuse_color = cor; o.data.materials.append(m); return o
# na cena a fachada fica em y = -0,1; aqui a face da fachada e y = 0
a = caixa("Janela_Moldura", (1.54, .1, 1.44), (0, -.02, 0), (.03, .03, .03, 1))
b = caixa("Janela_Vidro_Cortina", (1.4, .03, 1.3), (0, -.07, 0), (.55, .45, .33, 1))
for o in (a, b): o.select_set(True)
dst = os.path.join(OUT, "janela_sobrado.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[JANELA] %.0f KB" % (os.path.getsize(dst) / 1024))
