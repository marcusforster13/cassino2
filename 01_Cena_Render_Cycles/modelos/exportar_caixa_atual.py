"""Cassino clandestino - exporta a caixa registradora como esta na cena (modelo do autor + plasticos PBR + visor), para
o autor consertar. Uso: blender -b ../cassino.blend --python exportar_caixa_atual.py  ->  para_editar/caixa_registradora_atual.glb
Sai centrada, base em z = 0, com as teclas e o visor virados para -Y (como no arquivo que o autor mandou)."""
import bpy, os
from mathutils import Matrix
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
o = bpy.data.objects["Caixa_Registradora"]
o.data = o.data.copy(); o.matrix_world = Matrix.Identity(4)          # a malha ja e centrada; tira o giro da cena
for x in bpy.data.objects: x.select_set(False)
o.select_set(True); bpy.context.view_layer.objects.active = o
dst = os.path.join(OUT, "caixa_registradora_atual.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[CAIXA] %s, materiais %s, %.0f KB" % (o.name, [m.name for m in o.data.materials], os.path.getsize(dst) / 1024))
