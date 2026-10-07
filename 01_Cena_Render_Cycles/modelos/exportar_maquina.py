"""
Cassino clandestino - exporta UMA maquina caca-niquel para o autor refazer.

Uso:  blender -b ../cassino.blend --python exportar_maquina.py      (nao salva a cena)
Saida: modelos/para_editar/maquina_caca_niquel.glb

A maquina sai na origem, com a base no chao e a FRENTE voltada para -Y do Blender (a tela olha para -Y), sem a cadeira.
Tamanho atual: 60 cm de largura, 55 cm de profundidade, 1,73 m de altura (com o topo em arco).

Para devolver: salve como modelos/maquina_caca_niquel.glb, uma maquina so, na mesma posicao e de frente para -Y.
- Largura maxima de uns 62 cm: na cena elas ficam lado a lado, a cada 80 cm.
- A tela e uma peca separada chamada "..._Tela": se voce mantiver uma peca plana com "Tela" no nome, o script continua
  variando a imagem da tela de maquina para maquina; se nao, todas ficam com a sua tela.
"""
import bpy, bmesh, os

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)

def uv_simples(ob):
    me = ob.data
    if me.uv_layers: return
    bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.new("UVMap")
    vs = [v.co for v in bm.verts]
    if not vs: bm.free(); return
    mn = [min(v[i] for v in vs) for i in range(3)]; mx = [max(v[i] for v in vs) for i in range(3)]
    for f in bm.faces:
        n = f.normal; ax = max(range(3), key=lambda i: abs(n[i])); a, b = [i for i in range(3) if i != ax]
        for lp in f.loops:
            c = lp.vert.co
            lp[uv].uv = ((c[a] - mn[a]) / max(mx[a] - mn[a], 1e-6), (c[b] - mn[b]) / max(mx[b] - mn[b], 1e-6))
    bm.to_mesh(me); bm.free()

raiz = bpy.data.objects["Caca_Niquel_01"]
raiz.location = (0, 0, 0); raiz.rotation_euler = (0, 0, 0); bpy.context.view_layer.update()
pecas = [o for o in raiz.children_recursive if o.type == "MESH" and "_Cadeira_" not in o.name]
for o in bpy.data.objects: o.select_set(False)
for o in pecas:
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    uv_simples(o); o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = pecas[0]
dst = os.path.join(OUT, "maquina_caca_niquel.glb")
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
tris = 0
dg = bpy.context.evaluated_depsgraph_get()
for o in pecas:
    e = o.evaluated_get(dg); m = e.to_mesh(); tris += sum(len(p.vertices) - 2 for p in m.polygons); e.to_mesh_clear()
vs = [o.matrix_world @ v.co for o in pecas for v in o.data.vertices]
print("[MAQUINA] %d pecas, %d triangulos, de %s a %s, %.0f KB" % (len(pecas), tris, [round(min(v[i] for v in vs), 2) for i in range(3)], [round(max(v[i] for v in vs), 2) for i in range(3)], os.path.getsize(dst) / 1024))
print("[MAQUINA] pecas: " + ", ".join(sorted({o.name.replace("Caca_Niquel_01_", "").split(".")[0] for o in pecas})))
