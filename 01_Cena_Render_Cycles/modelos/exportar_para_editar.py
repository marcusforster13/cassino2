"""
Cassino clandestino - exporta pecas da cena para o autor melhorar no Blender e devolver.

Uso:  blender -b ../cassino.blend --python exportar_para_editar.py
Saida: modelos/para_editar/placas.glb e relogio.glb, NA MESMA POSICAO da cena.

Para devolver: salve o .glb editado em modelos/ com o mesmo nome (placas.glb, relogio.glb), sem mover as pecas de
lugar. O integrar_modelos.py troca as pecas antigas pelas novas (registradas em modelos.json).
"""
import bpy, bmesh, os, json

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)
GRUPOS = {
    "placas": ("Cartaz_Bar_", "Lousa_Precos", "Placa_Banheiro", "Cavalete_Bar", "Bar_Letreiro_", "Bar_Neon_Cerveja", "Placar_Acumulado",
               "Loja_Fechada_Aluga", "Extintor_Placa", "Calendario", "Quadro_Chaves"),
    "relogio": ("Relogio_",),
}
def uv_simples(ob):
    """UV de 0 a 1 em cada face (projecao pela direcao da face), para aceitar textura de imagem."""
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
registro = {}
for nome, prefixos in GRUPOS.items():
    objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(prefixos)]
    for o in bpy.data.objects: o.select_set(False)
    for o in objs:
        uv_simples(o); o.hide_set(False); o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, nome + ".glb"), export_format="GLB", use_selection=True, export_apply=True)
    registro[nome + ".glb"] = {"substitui": sorted({o.name for o in objs}), "colecao": objs[0].users_collection[0].name}
    print("[EDITAR] %s.glb: %d pecas (%s)" % (nome, len(objs), ", ".join(sorted({o.name.split(".")[0] for o in objs}))[:300]))
json.dump(registro, open(os.path.join(OUT, "registro_para_modelos_json.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
