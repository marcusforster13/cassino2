"""
Cassino clandestino - prepara os equipamentos do policial para o site (modelos fornecidos pelo usuario).

  arma.glb     pistola (180 pecas)  -> 1 malha, 21 cm de comprimento, cano para a frente, origem na empunhadura
  granada.glb  granada de efeito moral -> 1 malha, 13 cm de altura, origem no centro, textura de ate 512 px

Saida: ../../04_ThreeJS/web/modelos/arma.glb e granada.glb  (no site: frente = -Z, cima = +Y)
Uso:   blender -b --factory-startup --python preparar_equipamentos.py
"""
import bpy, os
from mathutils import Vector, Matrix

AQUI = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.normpath(os.path.join(AQUI, "..", "..", "04_ThreeJS", "web", "modelos"))
os.makedirs(WEB, exist_ok=True)

def say(m): print("[EQUIP] " + m)

def importar(arquivo):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(AQUI, arquivo))
    bpy.context.view_layer.update()
    return [o for o in bpy.data.objects if o.type == "MESH"]

def juntar(objs, nome):
    for o in objs:
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for o in bpy.data.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    with bpy.context.temp_override(active_object=objs[0], selected_objects=objs, selected_editable_objects=objs):
        bpy.ops.object.join()
    ob = objs[0]; ob.name = nome; ob.data.name = nome
    ob.data.transform(ob.matrix_world); ob.matrix_world = Matrix.Identity(4)
    for o in [o for o in bpy.data.objects if o is not ob]: bpy.data.objects.remove(o, do_unlink=True)
    return ob

def caixa(ob):
    vs = [v.co for v in ob.data.vertices]
    return Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))), Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))

def exportar(ob, nome):
    for o in bpy.data.objects: o.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.gltf(filepath=os.path.join(WEB, nome), export_format="GLB", use_selection=True,
                              export_image_format="JPEG", export_image_quality=85, export_animations=False)
    mn, mx = caixa(ob)
    say("%s: %d tris, caixa %s a %s" % (nome, sum(len(p.vertices) - 2 for p in ob.data.polygons), [round(v, 3) for v in mn], [round(v, 3) for v in mx]))

# ---------------------------------------------------------------- pistola
objs = importar("arma.glb")
boca = next(o for o in objs if o.name.startswith("Muzzle"))
boca_y = (boca.matrix_world @ Vector(boca.bound_box[0])).y
arma = juntar(objs, "Arma")
mn, mx = caixa(arma)
if abs(boca_y - mn.y) < abs(boca_y - mx.y):            # cano para -Y: vira para +Y (frente no site)
    arma.data.transform(Matrix.Rotation(3.14159265, 4, "Z")); mn, mx = caixa(arma)
k = .21 / (mx.y - mn.y)
arma.data.transform(Matrix.Scale(k, 4)); mn, mx = caixa(arma)
# origem na empunhadura: meio do punho (parte de baixo e de tras), para a mao/controle segurar ali
arma.data.transform(Matrix.Translation((-(mn.x + mx.x) / 2, -(mn.y + (mx.y - mn.y) * .22), -(mn.z + (mx.z - mn.z) * .45))))
for p in arma.data.polygons: p.use_smooth = False
arma["boca"] = [0, caixa(arma)[1].y, caixa(arma)[1].z - .012]
exportar(arma, "arma.glb")
say("boca do cano (Blender): %s" % [round(v, 3) for v in arma["boca"]])

# ---------------------------------------------------------------- granada de efeito moral
objs = importar("granada.glb")
for img in bpy.data.images:
    if img.size[0] > 512: img.scale(512, 512)
gr = juntar(objs, "Granada")
mn, mx = caixa(gr)
k = .13 / (mx.z - mn.z)
gr.data.transform(Matrix.Scale(k, 4)); mn, mx = caixa(gr)
gr.data.transform(Matrix.Translation(-(mn + mx) / 2))
exportar(gr, "granada.glb")
