"""Cassino clandestino - exporta a porta de aco de enrolar fechada (Bar_Porta_Loja_Fechada, ao lado da entrada do bar,
debaixo do neon CERVEJA GELADA) para o autor refazer. Uso: blender -b ../cassino.blend --python exportar_porta_enrolar.py
-> para_editar/porta_enrolar.glb. Sai como esta na cena, com a textura de ripas: 3 m de largura, 2,7 m de altura e 6 cm
de espessura, centrada em X e Y, base no chao (z = 0) e de frente para -Y (a rua; a fachada fica do lado +Y)."""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, "para_editar")
ob = bpy.data.objects["Bar_Porta_Loja_Fechada"]
for o in bpy.data.objects: o.select_set(False)
mw = ob.matrix_world.copy(); ob.parent = None; ob.data = ob.data.copy(); ob.data.transform(mw); ob.matrix_world.identity()
vs = [v.co for v in ob.data.vertices]; c = [(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(2)]; z0 = min(v.z for v in vs)
for v in ob.data.vertices: v.co.x -= c[0]; v.co.y -= c[1]; v.co.z -= z0
import bmesh                                  # a cena projeta a textura sem UV (1 repeticao por metro): grava essa projecao como UV
bm = bmesh.new(); bm.from_mesh(ob.data); uv = bm.loops.layers.uv.new("UVMap")
for f in bm.faces:
    ax = max(range(3), key=lambda i: abs(f.normal[i])); a_, b_ = [i for i in range(3) if i != ax]
    for lp in f.loops: lp[uv].uv = (lp.vert.co[a_], lp.vert.co[b_])
bm.to_mesh(ob.data); bm.free()
ob.name = "Porta_Enrolar"; ob.hide_set(False); ob.select_set(True); bpy.context.view_layer.objects.active = ob
dst = os.path.join(OUT, "porta_enrolar.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
print("[PORTA] %.0f KB, %d faces, UV: %s" % (os.path.getsize(dst) / 1024, len(ob.data.polygons), bool(ob.data.uv_layers)))
