"""
Cassino clandestino - exporta varias pecas simples da cena, uma por arquivo, para o autor refazer.

Uso:  blender -b ../cassino.blend --python exportar_varios.py      (nao salva a cena)
Saida: modelos/para_editar/<nome>.glb

Cada peca sai centrada na origem, com a base no chao (z = 0) e NA MESMA ORIENTACAO em que esta na cena.
Para devolver: salve com o mesmo nome em modelos/, centrada, base em z = 0, sem girar.
"""
import bpy, os
from mathutils import Matrix

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)

GRUPOS = {                                        # arquivo -> prefixos dos nomes (so o primeiro conjunto, sem ".001")
    "notebook": ("I_Notebook_",), "celular": ("I_Celular_",), "contadora_notas": ("Contadora_Notas",), "maquininha_cartao": ("Maquininha_Cartao",),
    "monitor_cameras": ("Monitor_Cameras",), "gravador_cameras": ("I_DVR_Cameras_",), "caderno_apostas": ("I_Caderno_Apostas_",),
    "cadeira_escritorio": ("Cadeira_Escritorio_",), "mesa_escritorio": ("Mesa_Escritorio_",), "mesa_carteado": ("Mesa_Carteado_",),
    "cadeira_carteado": ("Cadeira_Jogo_",), "cadeira_maquina": ("Caca_Niquel_01_Cadeira_",),
}
for arq, prefs in GRUPOS.items():
    pecas = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(prefs) and "." not in o.name[-4:]]
    if arq == "cadeira_maquina": pecas = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(prefs)]
    if not pecas: print("[EXPORTA] %s: nada encontrado" % arq); continue
    for o in pecas:
        mw = o.matrix_world.copy(); o.parent = None; o.data = o.data.copy(); o.data.transform(mw); o.matrix_world = Matrix.Identity(4)
    vs = [v.co for o in pecas for v in o.data.vertices]
    cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2; cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2; z0 = min(v.z for v in vs)
    for o in pecas: o.data.transform(Matrix.Translation((-cx, -cy, -z0)))
    for x in bpy.data.objects: x.select_set(False)
    for o in pecas: o.hide_set(False); o.select_set(True)
    bpy.context.view_layer.objects.active = pecas[0]
    dst = os.path.join(OUT, arq + ".glb")
    bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_apply=True)
    vs = [v.co for o in pecas for v in o.data.vertices]
    print("[EXPORTA] %s.glb: %d pecas, %d triangulos, %s cm" % (arq, len(pecas), sum(len(p.vertices) - 2 for o in pecas for p in o.data.polygons),
          " x ".join("%.0f" % ((max(v[i] for v in vs) - min(v[i] for v in vs)) * 100) for i in range(3))))
