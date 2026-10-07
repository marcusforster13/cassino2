"""
Cassino clandestino - gera a garrafa da cena num arquivo proprio, para o autor refazer.

Saida: modelos/para_editar/garrafa.glb  - garrafa de 29 cm de altura e 7,2 cm de diametro, base na origem, em pe (Z para cima
no Blender), com UV cilindrica (U = volta em torno da garrafa, V = altura), pronta para receber rotulo.

Para devolver: salve como modelos/garrafa.glb (uma garrafa, base na origem, mesma altura). O cassino.py usa esse modelo em
TODAS as garrafas da cena (cerca de 80). Se quiser variar, mande tambem garrafa_2.glb e garrafa_3.glb: sao sorteadas.
Mantenha cada garrafa leve (ate uns 300 triangulos): sao muitas copias.

Uso:  blender -b --factory-startup --python gerar_garrafa.py
"""
import bpy, bmesh, math, os

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "para_editar"); os.makedirs(OUT, exist_ok=True)
PERFIL = [(0, 0), (.034, 0), (.036, .006), (.036, .165), (.032, .185), (.016, .225), (.013, .235), (.013, .28), (.015, .283), (.015, .29), (0, .29)]
SEG = 20
bpy.ops.wm.read_factory_settings(use_empty=True)
bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
aneis = [[bm.verts.new((r * math.cos(2 * math.pi * k / SEG), r * math.sin(2 * math.pi * k / SEG), z)) for r, z in PERFIL] for k in range(SEG)]
for k in range(SEG):
    A, B = aneis[k], aneis[(k + 1) % SEG]
    for i in range(len(PERFIL) - 1):
        try: f = bm.faces.new((A[i], B[i], B[i + 1], A[i + 1]))
        except ValueError: continue
        for lp, (kk, ii) in zip(f.loops, ((k, i), (k + 1, i), (k + 1, i + 1), (k, i + 1))):
            lp[uv].uv = (kk / SEG, PERFIL[ii][1] / .29)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("Garrafa"); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth = True
m = bpy.data.materials.new("Garrafa_Vidro"); b = m.node_tree.nodes.get("Principled BSDF")
b.inputs["Base Color"].default_value = (.12, .06, .02, 1); b.inputs["Roughness"].default_value = .1
me.materials.append(m)
ob = bpy.data.objects.new("Garrafa", me); bpy.context.scene.collection.objects.link(ob)
ob.select_set(True); bpy.context.view_layer.objects.active = ob
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "garrafa.glb"), export_format="GLB", use_selection=True)
print("[GARRAFA] garrafa.glb: %d triangulos" % sum(len(p.vertices) - 2 for p in me.polygons))
