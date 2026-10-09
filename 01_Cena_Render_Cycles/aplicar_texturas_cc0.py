"""
Cassino clandestino - aplica as texturas CC0 (Poly Haven) na CENA PRINCIPAL (Cycles).

Uso:  blender -b cassino.blend --python aplicar_texturas_cc0.py
      (ou abrir o .blend, aba Scripting > Open > Run Script, e salvar)

- Materiais PBR com projecao em caixa (coordenadas do objeto, em metros): nao precisa de UV.
- Cor + rugosidade + relevo (mapa de deslocamento como Bump).
- Cada material recebe as propriedades "cc0_pasta" e "cc0_tile"; os pipelines de VR e
  three.js leem isso para converter para UV e glTF.
- Pode rodar de novo quantas vezes quiser (reconstroi os materiais a partir da tabela).
- As texturas ficam em ../04_ThreeJS/texturas_cc0 e sao referenciadas por caminho relativo.
"""
import bpy, os
import numpy as np

try:
    AQUI = os.path.dirname(os.path.abspath(__file__))
except NameError:
    AQUI = ""
if not os.path.isdir(os.path.join(AQUI, "..", "04_ThreeJS", "texturas_cc0")):
    AQUI = os.path.join(os.path.expanduser("~"), "Downloads", "cassino", "01_Cena_Render_Cycles")
TEX = os.path.normpath(os.path.join(AQUI, "..", "04_ThreeJS", "texturas_cc0"))

def hx(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))

def lin(c):
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c)

def arquivos(pasta):
    d = os.path.join(TEX, pasta); fs = sorted(os.listdir(d))
    pick = lambda k: next((os.path.join(d, f) for f in fs if k in f.lower()), None)
    return pick("_diff") or pick("_col"), pick("_rough"), pick("_disp")

def grafite(path):
    """Versao grafite do metal verde (mantem arranhoes e ferrugem). Salva junto das texturas."""
    out = os.path.join(os.path.dirname(path), "metal_grafite_diff.png")
    if not os.path.exists(out):
        src = bpy.data.images.load(path)
        w, h = src.size; px = np.empty(w * h * 4, np.float32); src.pixels.foreach_get(px)
        px = px.reshape(-1, 4); rgb = px[:, :3]
        g = (rgb @ np.array([.3, .59, .11]))[:, None]
        rgb = np.clip(g + (rgb - g) * .18, 0, 1) / max(g.mean(), 1e-3) * .5
        px[:, :3] = np.clip(rgb, 0, 1)
        dst = bpy.data.images.new("_tmp_grafite", w, h, alpha=False)
        dst.pixels.foreach_set(px.ravel()); dst.filepath_raw = out; dst.file_format = "PNG"; dst.save()
        bpy.data.images.remove(src); bpy.data.images.remove(dst)
    return out

def neutro(path):
    """Tecido em tom neutro e claro (sem cor), para tingir com a cor de cada estofado."""
    out = os.path.join(os.path.dirname(path), "tecido_neutro_cor.png")
    if not os.path.exists(out):
        src = bpy.data.images.load(path)
        w, h = src.size; px = np.empty(w * h * 4, np.float32); src.pixels.foreach_get(px)
        px = px.reshape(-1, 4); g = (px[:, :3] @ np.array([.3, .59, .11]))[:, None]
        px[:, :3] = np.clip(g / max(g.mean(), 1e-3) * .78, 0, 1)
        dst = bpy.data.images.new("_tmp_neutro", w, h, alpha=False)
        dst.pixels.foreach_set(px.ravel()); dst.filepath_raw = out; dst.file_format = "PNG"; dst.save()
        bpy.data.images.remove(src); bpy.data.images.remove(dst)
    return out

def carregar(path, dados):
    img = bpy.data.images.load(path, check_existing=True)
    try:
        img.filepath = bpy.path.relpath(path)
    except ValueError:
        pass
    if dados:
        img.colorspace_settings.name = "Non-Color"
    return img

def media_linear(img):
    w, h = img.size; px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px)
    m = px.reshape(-1, 4)[::7, :3].mean(0)
    return lin(tuple(m))

def pbr_caixa(mat, pasta, tile, tint=None, recolor=None, relevo=.35, metal=0.0):
    diff, rough, disp = arquivos(pasta)
    if recolor:
        diff = recolor(diff)
    alvo = lin(hx(tint)) if tint else tuple(mat.diffuse_color[:3])
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None) or nt.nodes.new("ShaderNodeBsdfPrincipled")
    for n in list(nt.nodes):
        if n not in (b, out):
            nt.nodes.remove(n)
    for inp in b.inputs:
        for l in list(inp.links):
            nt.links.remove(l)
    if not out.inputs["Surface"].is_linked:
        nt.links.new(b.outputs[0], out.inputs["Surface"])
    L = nt.links.new
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / tile,) * 3
    L(tc.outputs["Object"], mp.inputs["Vector"])
    def tex(path, dados):
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = carregar(path, dados)
        t.projection = "BOX"; t.projection_blend = .2
        L(mp.outputs["Vector"], t.inputs["Vector"])
        return t
    td = tex(diff, False)
    fator = [min(1.0, a / max(m, 1e-3)) for a, m in zip(alvo, media_linear(td.image))]
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    next(i for i in mix.inputs if i.name == "Factor" and i.type == "VALUE").default_value = 1.0
    L(td.outputs["Color"], next(i for i in mix.inputs if i.name == "A" and i.type == "RGBA"))
    next(i for i in mix.inputs if i.name == "B" and i.type == "RGBA").default_value = (*fator, 1)
    L(next(o for o in mix.outputs if o.name == "Result" and o.type == "RGBA"), b.inputs["Base Color"])
    if rough:
        tr = tex(rough, True); sep = nt.nodes.new("ShaderNodeSeparateColor")
        L(tr.outputs["Color"], sep.inputs["Color"]); L(sep.outputs["Green"], b.inputs["Roughness"])
    if disp:
        tdp = tex(disp, True); bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = relevo; bp.inputs["Distance"].default_value = .02
        L(tdp.outputs["Color"], bp.inputs["Height"]); L(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Metallic"].default_value = metal
    mat["cc0_metal"] = float(metal)
    mat["cc0_pasta"] = pasta
    mat["cc0_tile"] = float(tile)
    mat["cc0_tint"] = list(alvo)
    mat["cc0_recolor"] = recolor.__name__ if recolor else ""

# nome do material -> (pasta, tile em metros, cor alvo, recolor, forca do relevo)
TABELA = {
    "Asfalto":            ("asfalto", 3.0, "#3a3a3c", None, .5),
    "Meio_Fio_Concreto":  ("concreto", 1.5, None, None, .35),
    "Concreto_Aparente":  ("concreto", 2.0, None, None, .25),
    "Fachada_Areia":      ("reboco_pintado", 2.0, None, None, .25),
    "Fachada_Branca":     ("reboco_pintado", 2.0, None, None, .25),
    "Fachada_Terracota":  ("reboco_pintado", 2.0, None, None, .25),
    "Fachada_Cinza":      ("concreto", 2.0, None, None, .2),
    "Fachada_Bar":        ("reboco_pintado", 2.0, None, None, .3),
    "Reboco_Interno":     ("reboco", 2.0, None, None, .25),
    "Muro_Reboco":        ("reboco", 2.0, None, None, .4),
    "Laje_Teto":          ("reboco", 2.5, None, None, .15),
    "Piso_Cimento":       ("concreto", 2.0, None, None, .2),
    "Piso_Taco_Salao":    ("piso_madeira", 1.6, "#8a6a48", None, .25),
    "Madeira_Balcao":     ("madeira_escura", 1.2, "#5a3a26", None, .15),
    "Madeira_Clara":      ("madeira_tabuas", 1.2, "#9a7650", None, .2),
    "Madeira_Roleta":     ("madeira_pinho", .7, "#ffffff", None, .15),
    "Inox_Balde":         ("metal_inox", .3, "#ffffff", None, .1),
    "Plastico_Caixa":     ("plastico_preto", .25, "#ffffff", None, .1),      # Plastic012B, 015A e 017A (ambientCG, CC0), enviadas pelo autor
    "Plastico_Botao_Azul": ("plastico_azul", .1, "#ffffff", None, .05),
    "Plastico_Botao_Verde": ("plastico_verde", .1, "#ffffff", None, .05),
    "Aco_Cofre":          ("metal_cofre", .6, "#ffffff", None, .1),         # Metal041A (ambientCG, CC0), enviada pelo autor          # Metal055A (ambientCG, CC0), enviada pelo autor      # coated_pine, enviada pelo autor: cor natural
    "Porta_Madeira":      ("madeira_escura", 1.4, "#6b4a30", None, .15),
    "Couro_Vinho":        ("couro", .6, "#5a1c1c", None, .3),
    "Feltro_Verde":       ("tecido", .4, "#1f6b3a", neutro, .15),
    "Cortina_Branca":     ("tecido", .5, "#d9d6cc", neutro, .35),
    "Veludo_Vinho":       ("tecido", .5, "#6a1a2c", neutro, .3),
    "Feltro_Sinuca":      ("tecido", .4, "#1c5c8a", neutro, .15),
    "Poste_Metal":        ("metal_pintado", 1.0, "#3b3d40", grafite, .15),
    "Porta_Loja_Metal":   ("metal_pintado", 1.0, "#5b5f66", grafite, .15),
    "Porta_Ferro":        ("metal_pintado", 1.0, "#4a4f55", grafite, .2),
}
METAL = {"Inox_Balde": .5, "Aco_Cofre": .35}      # brilho de metal moderado: metal puro fica preto no site, a noite
feitos = []
for nome, (pasta, tile, tint, rec, relevo) in TABELA.items():
    m = bpy.data.materials.get(nome)
    if m and os.path.isdir(os.path.join(TEX, pasta)):
        pbr_caixa(m, pasta, tile, tint, rec, relevo, METAL.get(nome, 0.0)); feitos.append(nome)
print("[CC0] %d materiais com texturas Poly Haven: %s" % (len(feitos), ", ".join(feitos)))
if bpy.app.background:
    bpy.ops.wm.save_mainfile()
    print("[CC0] cena principal salva")
