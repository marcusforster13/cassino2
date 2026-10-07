"""
Cassino clandestino - gera o maco de notas para receber textura de imagem.

Saidas nesta pasta:
  maco_de_notas.glb          maco de 15,6 x 6,5 x 2,2 cm (tamanho de uma nota de 100 reais), com UV e a imagem-modelo aplicada
  maco_de_notas_modelo.png   imagem-modelo 1024 x 1024: pinte por cima e salve como maco_de_notas_textura.png

Regioes da imagem (de cima para baixo):
  VERDE  (42% de cima)   frente da nota  - aparece na face de cima do maco      1024 x 430 px
  AZUL   (42% do meio)   verso da nota   - aparece na face de baixo             1024 x 430 px
  BEGE   (faixa de baixo) lateral do maco - bordas das notas empilhadas; ja vem pronta, nao precisa mexer

Uso:  blender -b --factory-startup --python gerar_maco_de_notas.py
"""
import bpy, bmesh, os
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
S = 1024
V_FRENTE = (.58, 1.0); V_VERSO = (.16, .58); V_LADO = (0.0, .12)

# ---- imagem-modelo
a = np.ones((S, S, 4), np.float32)
yy, xx = np.mgrid[0:S, 0:S]; v = 1 - yy / S                       # v = 1 no topo da imagem
def regiao(vr): return (v >= vr[0]) & (v < vr[1])
a[regiao(V_FRENTE), :3] = (.45, .68, .52)                          # frente: verde
a[regiao(V_VERSO), :3] = (.42, .56, .74)                           # verso: azul
a[regiao((.12, .16)), :3] = (.2, .2, .2)                           # separador
lado = regiao(V_LADO)
r = np.random.default_rng(7)
linhas = (.86 + .1 * np.sin(yy * 2.9) + .03 * r.standard_normal((S, 1)))[..., None] * np.array((.93, .9, .82))
a[lado, :3] = np.broadcast_to(np.clip(linhas, 0, 1), (S, S, 3))[lado]
for vr in (V_FRENTE, V_VERSO):                                     # moldura clara para mostrar o limite de cada nota
    m = regiao(vr); borda = m & ((xx < 6) | (xx >= S - 6) | (np.abs(v - vr[0]) < .006) | (np.abs(v - vr[1]) < .006))
    a[borda, :3] = (.95, .95, .9)
bpy.ops.wm.read_factory_settings(use_empty=True)
img = bpy.data.images.new("maco_de_notas_modelo", S, S, alpha=False)
img.pixels.foreach_set(np.flipud(a).ravel()); img.filepath_raw = os.path.join(AQUI, "maco_de_notas_modelo.png"); img.file_format = "PNG"; img.save()

# ---- malha com UV
L, P, H = .156, .065, .022
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(L, P, H), verts=bm.verts)
uv = bm.loops.layers.uv.new("UVMap")
for f in bm.faces:
    n = f.normal
    for lp in f.loops:
        c = lp.vert.co; u = c.x / L + .5
        if n.z > .5:   lp[uv].uv = (u, V_FRENTE[0] + (c.y / P + .5) * (V_FRENTE[1] - V_FRENTE[0]))
        elif n.z < -.5: lp[uv].uv = (1 - u, V_VERSO[0] + (c.y / P + .5) * (V_VERSO[1] - V_VERSO[0]))
        else:
            t = (c.y / P + .5) if abs(n.x) > .5 else u               # ao longo da lateral
            lp[uv].uv = (t, V_LADO[0] + (c.z / H + .5) * (V_LADO[1] - V_LADO[0]))
me = bpy.data.meshes.new("Maco_de_Notas"); bm.to_mesh(me); bm.free()
mat = bpy.data.materials.new("Img_Maco_de_Notas"); nt = mat.node_tree; b = nt.nodes.get("Principled BSDF")
t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .85
me.materials.append(mat)
ob = bpy.data.objects.new("Maco_de_Notas", me); bpy.context.scene.collection.objects.link(ob)
ob.select_set(True); bpy.context.view_layer.objects.active = ob
bpy.ops.export_scene.gltf(filepath=os.path.join(AQUI, "maco_de_notas.glb"), export_format="GLB", use_selection=True, export_image_format="AUTO")
print("[MACO] maco_de_notas.glb e maco_de_notas_modelo.png gerados em " + AQUI)
