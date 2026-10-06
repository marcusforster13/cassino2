"""
Cassino clandestino - cena base para Blender 5.x (gera cassino.blend do zero)

Rua do Rio de Janeiro, a noite: bar de fachada aberto ao publico, porta "PRIVATIVO" para os fundos, corredor,
salao de jogos (caca-niqueis, carteado, roleta), escritorio/caixa trancado, depositos, quintal e beco lateral
(rota de fuga). Viatura da PM na rua. Objetos I_* sao interativos (portas e material a apreender);
vazios P_* sao pontos usados pelo site (personagens, maquinas, rotas).

Uso:  blender -b --factory-startup --python cassino.py
Unidades em metros. X = ao longo da rua, Y = para dentro do predio, Z = para cima.
Sem logotipos de marcas e sem brasoes oficiais: ha um espaco "Brasao_(inserir_imagem_oficial)".
Os equipamentos de jogo sao desenho proprio e generico, sem reproduzir fabricantes.
"""
import bpy, bmesh, math, random, os
import numpy as np
from mathutils import Vector, Matrix

PI = math.pi
rnd = random.Random(2026)
try:
    AQUI = os.path.dirname(os.path.abspath(__file__))
except NameError:
    AQUI = os.path.join(os.path.expanduser("~"), "Downloads", "cassino", "01_Cena_Render_Cycles")

def say(m): print("[CASSINO] " + m)

# ------------------------------------------------------------------ limpeza
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
scene = bpy.context.scene

def collection(name):
    c = bpy.data.collections.new(name); scene.collection.children.link(c); return c

# ------------------------------------------------------------------ materiais
def hx(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
def lin(c): return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c)

def mat(name, color, rough=.8, metal=0., emit=None, forca=0., alpha=None):
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes.get("Principled BSDF")
    c = lin(hx(color))
    b.inputs["Base Color"].default_value = (*c, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*lin(hx(emit)), 1)
        b.inputs["Emission Strength"].default_value = forca
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
            try: setattr(m, attr, val)
            except Exception: pass
    m.diffuse_color = (*c, 1 if alpha is None else alpha)
    return m

def np_image(name, arr):
    h, w, _ = arr.shape
    rgba = np.ones((h, w, 4), dtype=np.float32); rgba[..., :3] = arr
    img = bpy.data.images.new(name, w, h, alpha=False)
    img.pixels.foreach_set(np.flipud(rgba).ravel()); img.pack()
    return img

def img_mat(name, img, tile_m, rough=.6):
    """Textura gerada, projetada em caixa (coordenadas do objeto, em metros)."""
    m = bpy.data.materials.new(name); nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / tile_m,) * 3
    tex.projection = "BOX"; tex.projection_blend = .1
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (.5, .5, .5, 1)
    return m

def tex_calcada(S=512):
    """Calcada de pedra portuguesa com ondas pretas e brancas (padrao tradicional carioca, desenho proprio)."""
    y, x = np.mgrid[0:S, 0:S] / S
    onda = np.sin((y + .12 * np.sin(x * 2 * PI)) * 2 * PI * 2)
    r = np.random.default_rng(5)
    branco, preto = np.array(hx("#d9d4c8")), np.array(hx("#2b2a28"))
    a = np.where((onda > 0)[..., None], branco, preto).astype(np.float64)
    cel = 16; g = r.uniform(.86, 1.06, (S // cel, S // cel, 1)); a *= np.kron(g, np.ones((cel, cel, 1)))
    yy, xx = np.mgrid[0:S, 0:S]
    a[(xx % cel == 0) | (yy % cel == 0)] *= .72            # juntas das pedrinhas
    return np.clip(a, 0, 1)

M = {
    "asfalto": mat("Asfalto", "#3a3a3c", .9),
    "faixa": mat("Pintura_Viaria_Branca", "#d8d6cc", .7),
    "faixa_am": mat("Pintura_Viaria_Amarela", "#d9a514", .7),
    "meiofio": mat("Meio_Fio_Concreto", "#9c988f", .95),
    "calcada": img_mat("Calcada_Portuguesa", np_image("calcada_portuguesa", tex_calcada()), 2.4, .75),
    "concreto": mat("Concreto_Aparente", "#a19d95", .95),
    "reboco_a": mat("Fachada_Areia", "#cdbf9f", .92), "reboco_b": mat("Fachada_Branca", "#dedad0", .92),
    "reboco_c": mat("Fachada_Terracota", "#a8684a", .92), "reboco_d": mat("Fachada_Cinza", "#8f9196", .92),
    "janela_on": mat("Janela_Acesa", "#3a3020", .4, emit="#ffc98a", forca=1.1),
    "janela_on2": mat("Janela_Acesa_Fria", "#20303a", .4, emit="#bcd8ff", forca=.8),
    "janela_off": mat("Janela_Apagada", "#10151c", .15),
    "loja": mat("Porta_Loja_Metal", "#5b5f66", .5, .6),
    "tronco": mat("Tronco_Arvore", "#5c4b3c", 1), "folha": mat("Folhagem", "#2c5230", .8),
    "terra": mat("Terra_Canteiro", "#4a3a2c", 1),
    "poste": mat("Poste_Metal", "#3b3d40", .5, .6),
    "lamp": mat("Luminaria_Publica", "#ffffff", .4, emit="#ffd9a0", forca=25),
    "led": mat("Refletor_LED", "#ffffff", .4, emit="#f4f7ff", forca=40),
    "tripe": mat("Tripe_Amarelo", "#d6a410", .45, .3),
    "preto": mat("Preto_Fosco", "#17181a", .6), "preto_b": mat("Preto_Brilhante", "#0c0c0d", .2),
    "branco": mat("Plastico_Branco", "#eceae4", .45),
    "azul": mat("Lona_Azul", "#1c3fa8", .6), "azul_claro": mat("Azul_Faixa", "#2a66d8", .5),
    "lona_balao": mat("Balao_Branco", "#f2f2ee", .5, emit="#ffffff", forca=1.6),
    "lona_balao_az": mat("Balao_Azul", "#1c3fa8", .5, emit="#2a55d0", forca=.9),
    "texto_az": mat("Texto_Azul", "#16307f", .6), "texto_br": mat("Texto_Branco", "#f4f4f0", .6),
    "texto_pr": mat("Texto_Preto", "#111111", .6),
    "cone": mat("Cone_Laranja", "#e8500e", .55), "refletivo": mat("Faixa_Refletiva", "#f1f1ec", .3),
    "metal": mat("Metal_Escovado", "#8a8c8e", .35, 1), "cromo": mat("Cromado", "#c9ccd0", .15, 1),
    "pneu": mat("Borracha_Pneu", "#141414", .9), "disco": mat("Disco_Freio", "#5a5c5e", .4, .8),
    "aro": mat("Roda_Liga", "#9a9da2", .32, .85), "aro_aco": mat("Roda_Aco", "#2a2b2d", .5, .6),
    "vidro": mat("Vidro_Carro_Fume", "#1a2228", .05, alpha=.35),
    "plast": mat("Plastico_Preto_Texturizado", "#1d1e20", .75),
    "interior": mat("Interior_Carro", "#2a2b2e", .8),
    "farol": mat("Farol_Aceso", "#ffffff", .2, emit="#fff4d8", forca=6),
    "lanterna": mat("Lanterna_Acesa", "#5a0a08", .3, emit="#ff1808", forca=3),
    "placa": mat("Placa_Mercosul", "#f2f2f2", .5), "placa_azul": mat("Placa_Faixa_Azul", "#1b3f9c", .5),
    "pint_pm": mat("Viatura_Pintura_Branca", "#e9eaec", .3), "faixa_pm": mat("Viatura_Faixa_Azul", "#1e4fb8", .3),
    "pint_van": mat("Van_Pintura_Branca", "#eceded", .3),
    "pint_cinza": mat("Carro_Pintura_Cinza", "#8d9096", .3, .15), "pint_branca": mat("Carro_Pintura_Branca", "#e6e6e4", .3),
    "pint_guincho": mat("Guincho_Pintura_Branca", "#e2e3e3", .35),
    "plataforma": mat("Guincho_Plataforma", "#4a4f55", .55, .7),
    "giro_verm": mat("Giroflex_Vermelho", "#5a0a08", .2, emit="#ff1010", forca=.05),
    "giro_azul": mat("Giroflex_Azul", "#08205a", .2, emit="#1040ff", forca=.05),
    "ambar": mat("Sinalizador_Ambar", "#7a4a05", .2, emit="#ffa010", forca=4),
    "brasao": mat("Brasao_(inserir_imagem_oficial)", "#c8cbd0", .5),
    "colete": mat("Colete_Refletivo", "#d7e21b", .6),
    "tela": mat("Tela_Acesa", "#000000", .2, emit="#9fc4ff", forca=2.5),
    "tela_verde": mat("Visor_Etilometro", "#000000", .2, emit="#8dffb0", forca=2.0),
    "maleta": mat("Maleta_Preta", "#1a1b1d", .55), "espuma": mat("Espuma_Maleta", "#2e3033", 1),
    "papel": mat("Papel", "#f6f3ea", .9), "bocal": mat("Bocal_Embalado", "#e8f0f4", .35),
    "barreira": mat("Barreira_Laranja", "#e2520f", .5),
}

# ------------------------------------------------------------------ geometria
def finish(name, bm, loc, mats, col, parent=None, rot=(0, 0, 0), smooth=False, bevel=0.0, seg=2):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = smooth
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]): me.materials.append(m)
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    if parent: ob.parent = parent
    ob.location = loc; ob.rotation_euler = rot
    if bevel:
        b = ob.modifiers.new("Chanfro", "BEVEL"); b.width = bevel; b.segments = seg; b.limit_method = "ANGLE"
        for p in me.polygons: p.use_smooth = True
    return ob

def box(name, tam, pos, m, col, parent=None, rot=(0, 0, 0), bevel=0.0, seg=2):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=Vector(tam), verts=bm.verts)
    return finish(name, bm, pos, m, col, parent, rot, bevel=bevel, seg=seg)

def cyl(name, r1, r2, h, pos, m, col, parent=None, rot=(0, 0, 0), seg=20):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=h)
    return finish(name, bm, pos, m, col, parent, rot, smooth=True)

def barra(name, a, b, r, m, col, parent=None, seg=10):
    """Cilindro fino entre dois pontos."""
    a, b = Vector(a), Vector(b); d = b - a
    ob = cyl(name, r, r, d.length, (a + b) / 2, m, col, parent, seg=seg)
    ob.rotation_euler = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler()
    return ob

def torno(name, perfil, mats, col, parent=None, pos=(0, 0, 0), rot=(0, 0, 0), seg=32, idx=None):
    """Solido de revolucao em torno de Z (perfil = [(raio, z), ...]); idx = material de cada segmento do perfil."""
    bm = bmesh.new(); aneis = []
    for k in range(seg):
        a = 2 * PI * k / seg
        aneis.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in perfil])
    for k in range(seg):
        A, B = aneis[k], aneis[(k + 1) % seg]
        for i in range(len(perfil) - 1):
            try:
                f = bm.faces.new((A[i], B[i], B[i + 1], A[i + 1]))
                if idx: f.material_index = idx[i]
            except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, pos, mats, col, parent, rot, smooth=True)

def malha(name, verts, faces, m, col, parent=None, pos=(0, 0, 0), smooth=False, idx=None):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    bm = bmesh.new(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    if idx:
        bm.faces.ensure_lookup_table()
        for f, i in zip(bm.faces, idx): f.material_index = i
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, pos, m, col, parent, smooth=smooth)

def texto_malha(conteudo, tam, espaco=1.0):
    cu = bpy.data.curves.new("_txt", "FONT"); cu.body = conteudo; cu.size = tam; cu.align_x = "CENTER"; cu.align_y = "CENTER"
    cu.resolution_u = 2; cu.space_character = espaco
    tmp = bpy.data.objects.new("_txt_tmp", cu); scene.collection.objects.link(tmp)
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp, do_unlink=True); bpy.data.curves.remove(cu)
    return me

# para onde o texto fica virado (quem le esta desse lado)
VIRADO = {"-y": (PI / 2, 0, 0), "+y": (PI / 2, 0, PI), "-x": (PI / 2, 0, -PI / 2), "+x": (PI / 2, 0, PI / 2), "cima": (0, 0, 0)}
def texto(name, conteudo, tam, pos, virado, m, col, parent=None, espaco=1.0):
    me = texto_malha(conteudo, tam, espaco); me.name = name; me.materials.append(m)
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    if parent: ob.parent = parent
    ob.location = pos; ob.rotation_euler = VIRADO[virado] if isinstance(virado, str) else virado
    return ob

def vazio(name, pos, col, rz=0.0, parent=None):
    e = bpy.data.objects.new(name, None); col.objects.link(e); e.location = pos; e.rotation_euler = (0, 0, rz)
    e.empty_display_size = .4
    if parent: e.parent = parent
    return e

def luz(name, tipo, watts, cor, pos, col, parent=None, alvo=None, **kw):
    l = bpy.data.lights.new(name, tipo); l.energy = watts; l.color = lin(hx(cor))
    for k, v in kw.items(): setattr(l, k, v)
    ob = bpy.data.objects.new(name, l); col.objects.link(ob); ob.location = pos
    if parent: ob.parent = parent
    if alvo is not None:
        ob.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    return ob
def adesivo(name, ponto, nu, nv, col, parent=None, pos=(0, 0, 0), mat=None):
    """Adesivo com o logotipo sobre uma superficie curva: ponto(u, v) devolve a posicao 3D para u, v de 0 a 1."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    g = [[bm.verts.new(ponto(i / nu, j / nv)) for j in range(nv + 1)] for i in range(nu + 1)]
    for i in range(nu):
        for j in range(nv):
            f = bm.faces.new((g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1]))
            for lp, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                lp[uvl].uv = (a / nu, b / nv)
    ob = finish(name, bm, pos, mat or LOGO, col, parent, smooth=True)
    return ob
def tex_porta_enrolar(S=256):
    """Porta de aco de enrolar: ripas horizontais com sujeira."""
    y, x = np.mgrid[0:S, 0:S] / S
    ripa = (y * 12) % 1
    a = np.ones((S, S, 3)) * np.array(hx("#7b8087"))
    a *= (.72 + .28 * np.sin(ripa * PI) ** .5)[..., None]
    a[ripa < .08] *= .45
    r = np.random.default_rng(9); a *= (1 + .06 * r.standard_normal((S, S, 1)))
    a *= (1 - .25 * np.clip(y - .75, 0, 1) * 4)[..., None]          # mais sujo embaixo
    return np.clip(a, 0, 1)

def tex_pastilha(cor, S=256, n=20):
    """Revestimento de pastilhas, comum nos predios dos anos 60 e 70."""
    r = np.random.default_rng(int(sum(cor) * 1000))
    cel = S // n
    g = r.uniform(.84, 1.08, (n, n, 1)); a = np.kron(g, np.ones((cel, cel, 1))) * np.array(cor)
    a = np.pad(a, ((0, S - a.shape[0]), (0, S - a.shape[1]), (0, 0)), mode="edge")
    yy, xx = np.mgrid[0:S, 0:S]
    a[(xx % cel == 0) | (yy % cel == 0)] = np.array(hx("#8d8a84"))
    return np.clip(a, 0, 1)

M.update({
    "porta_enrolar": img_mat("Porta_Enrolar", np_image("porta_enrolar", tex_porta_enrolar()), 1.0, .45),
    "pastilha_a": img_mat("Pastilha_Verde", np_image("pastilha_verde", tex_pastilha(hx("#8fa89a"))), .5, .35),
    "pastilha_b": img_mat("Pastilha_Azul", np_image("pastilha_azul", tex_pastilha(hx("#8a9db5"))), .5, .35),
    "esquadria": mat("Esquadria_Aluminio", "#3a3d42", .4, .7),
    "ar_cond": mat("Ar_Condicionado", "#d6d4cc", .5),
    "vitrine": mat("Vitrine_Acesa", "#40382a", .2, emit="#ffe2b0", forca=2.2),
    "rodape": mat("Rodape_Granito", "#2e2d2c", .35),
    "caixa_dagua": mat("Caixa_Dagua", "#3b6fb5", .6),
    "guarda": mat("Guarda_Corpo_Metal", "#2b2d30", .5, .6),
    "vidro_var": mat("Vidro_Varanda", "#7fa0a8", .08, alpha=.3),
    "cortina": mat("Janela_Cortina", "#2a2622", .8, emit="#d9b98a", forca=.45),
})
M["texto_letreiro"] = mat("Texto_Letreiro", "#ffffff", .5, emit="#ffffff", forca=1.4)
LETREIROS = [mat("Letreiro_%d" % i, c, .5, emit=c, forca=.35) for i, c in enumerate(("#b3261e", "#1f5fa8", "#1e7a46", "#d98a12", "#5b2a86", "#222428"))]
LOJAS = ["FARMÁCIA", "PADARIA", "LANCHONETE", "MERCADINHO", "CHAVEIRO", "PAPELARIA", "ÓTICA", "BAR E PETISCOS", "LOTÉRICA", "CASA DE SUCOS",
         "BARBEARIA", "ARMARINHO", "AÇOUGUE", "FLORICULTURA", "LAVANDERIA", "SAPATARIA", "HORTIFRUTI", "ASSISTÊNCIA TÉCNICA"]
rnd.shuffle(LOJAS)
_loja = [0]

def predio(nome, x0, x1, y_frente, lado, altura, cor, andares, estilo):
    """estilo: 0 pilastras e janelas simples · 1 varandas de alvenaria · 2 faixas horizontais (modernista) · 3 varandas de vidro"""
    prof = 9.0; w = x1 - x0; xc = (x0 + x1) / 2; yc = y_frente + lado * prof / 2
    v = "-y" if lado > 0 else "+y"
    F = lambda d: y_frente - lado * d                       # d metros para fora da fachada (em direcao a rua)
    C = C_PRED
    box(nome, (w, prof, altura), (xc, yc, altura / 2 + .15), cor, C)
    # ---- terreo comercial
    box(nome + "_Rodape", (w, .08, .55), (xc, F(.03), .42), M["rodape"], C)
    nl = max(2, int(w // 4.3)); pl = w / nl
    for j in range(nl + 1):
        box(nome + "_Pilar", (.42, .16, 3.35), (min(max(x0 + pl * j, x0 + .21), x1 - .21), F(.07), 1.82), M["concreto"], C)
    for j in range(nl):
        x = x0 + pl * (j + .5); lv = pl - .62
        aberta = False                                         # todas as lojas fechadas (operacao noturna)
        if aberta:
            box(nome + "_Vitrine", (lv, .05, 2.55), (x, F(.02), 1.45), M["vitrine"], C)
            box(nome + "_Vitrine_Caixilho", (lv, .07, .08), (x, F(.04), 2.72), M["esquadria"], C)
            box(nome + "_Vitrine_Caixilho", (.07, .07, 2.55), (x + lv * .22, F(.04), 1.45), M["esquadria"], C)
        else:
            box(nome + "_Porta_Loja", (lv, .06, 3.22), (x, F(.02), 1.78), M["porta_enrolar"], C)
            box(nome + "_Porta_Loja_Guia", (lv + .1, .1, .16), (x, F(.04), 3.44), M["esquadria"], C)
    box(nome + "_Marquise", (w, 1.35, .16), (xc, F(.67), 3.66), M["concreto"], C)
    box(nome + "_Marquise_Testeira", (w, .06, .3), (xc, F(1.33), 3.6), M["concreto"], C)
    # ---- andares
    hand = (altura - 4.2) / andares; nj = max(2, int(w // 2.7)); passo = w / nj
    varanda = estilo in (1, 3)
    for a in range(andares):
        z0 = 4.35 + hand * a
        if estilo == 2:
            box(nome + "_Faixa_Peitoril", (w, .1, hand * .3), (xc, F(.04), z0 + hand * .14), M["concreto"], C)
        for j in range(nj):
            x = x0 + passo * (j + .5); r = rnd.random()
            m = M["janela_on"] if r < .17 else M["janela_on2"] if r < .23 else M["cortina"] if r < .34 else M["janela_off"]
            jw = passo * (.72 if estilo == 2 else .56); jh = hand * (.46 if estilo == 2 else .5); zc = z0 + hand * .56
            box(nome + "_Moldura", (jw + .14, .1, jh + .14), (x, F(.03), zc), M["esquadria"], C)
            box(nome + "_Janela", (jw, .03, jh), (x, F(.075), zc), m, C)
            box(nome + "_Janela_Montante", (.05, .04, jh), (x, F(.085), zc), M["esquadria"], C)
            if not varanda:
                box(nome + "_Peitoril", (jw + .3, .2, .07), (x, F(.1), zc - jh / 2 - .1), M["concreto"], C)
                if rnd.random() < .28:
                    box(nome + "_Ar_Cond", (.66, .42, .42), (x + rnd.uniform(-.2, .2) * jw, F(.2), zc - jh / 2 - .38), M["ar_cond"], C, bevel=.02)
                    box(nome + "_Ar_Cond_Grade", (.56, .02, .3), (x, F(.415), zc - jh / 2 - .38), M["esquadria"], C)
        if varanda:
            box(nome + "_Varanda_Laje", (w - .5, 1.05, .12), (xc, F(.52), z0 + .02), M["concreto"], C)
            if estilo == 1:
                box(nome + "_Varanda_Mureta", (w - .5, .1, .95), (xc, F(1.0), z0 + .55), cor, C)
            else:
                box(nome + "_Varanda_Vidro", (w - .5, .02, .85), (xc, F(1.02), z0 + .5), M["vidro_var"], C)
                box(nome + "_Varanda_Guarda", (w - .5, .05, .05), (xc, F(1.02), z0 + .97), M["guarda"], C)
            for k in range(1, nj):                               # divisorias entre os apartamentos
                box(nome + "_Varanda_Divisoria", (.08, 1.0, hand - .15), (x0 + passo * k, F(.5), z0 + hand / 2), cor, C)
    if estilo == 0:                                              # pilastras marcando a fachada
        for k in range(0, nj + 1, 2):
            box(nome + "_Pilastra", (.3, .12, altura - 4.2), (min(max(x0 + passo * k, x0 + .15), x1 - .15), F(.05), 4.2 + (altura - 4.2) / 2 + .15), M["concreto"], C)
    # ---- topo: cornija, platibanda, caixa d'agua e casa de maquinas
    box(nome + "_Cornija", (w + .1, .4, .22), (xc, F(.1), altura + .15), M["concreto"], C)
    box(nome + "_Platibanda", (w, .2, .7), (xc, F(-.1), altura + .5), cor, C)
    cx = xc + rnd.uniform(-.25, .25) * w
    box(nome + "_Casa_Maquinas", (3.0, 3.0, 2.2), (cx, yc, altura + 1.25), M["concreto"], C)
    cyl(nome + "_Caixa_Dagua", .85, .85, 1.3, (cx + rnd.choice((-2.6, 2.6)), yc + .5, altura + .8), M["caixa_dagua"], C, seg=14)
C_PRED = C_VEG = C_BLITZ = C_LUZ = None      # definidos abaixo
def poste(nome, x, y, lado):
    cyl(nome + "_Fuste", .07, .1, 8.4, (x, y, 4.35), M["poste"], C_VEG, seg=12)
    barra(nome + "_Braco", (x, y, 8.4), (x, y - lado * 2.2, 8.75), .045, M["poste"], C_VEG)
    box(nome + "_Luminaria", (.3, .7, .12), (x, y - lado * 2.4, 8.72), M["poste"], C_VEG, bevel=.03)
    box(nome + "_Difusor", (.22, .5, .02), (x, y - lado * 2.4, 8.65), M["lamp"], C_VEG)
    luz(nome + "_Luz", "POINT", 650, "#ffd9a0", (x, y - lado * 2.4, 8.5), C_LUZ, shadow_soft_size=.25)
def cadeira(nome, x, y, rz, col=C_BLITZ):
    r = vazio(nome, (x, y, 0), col, rz)
    box(nome + "_Assento", (.44, .44, .035), (0, 0, .44), M["branco"], col, r, bevel=.015)
    box(nome + "_Encosto", (.42, .03, .42), (0, .215, .7), M["branco"], col, r, rot=(-.14, 0, 0), bevel=.012)
    for sx in (-1, 1):
        box(nome + "_Braco", (.04, .4, .03), (sx * .22, .02, .64), M["branco"], col, r, bevel=.01)
        for sy in (-1, 1):
            barra(nome + "_Pe", (sx * .19, sy * .19, .44), (sx * .23, sy * .23, 0), .017, M["branco"], col, r, seg=6)
    return r

def mesa(nome, x, y, rz=0.0, tam=(1.2, .7), m=None, col=C_BLITZ, toalha=None):
    r = vazio(nome, (x, y, 0), col, rz); w, d = tam
    box(nome + "_Tampo", (w, d, .035), (0, 0, .725), m or M["branco"], col, r, bevel=.012)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(nome + "_Pe", .022, .022, .71, (sx * (w / 2 - .08), sy * (d / 2 - .08), .355), M["metal"], col, r, seg=8)
    if toalha:
        box(nome + "_Toalha", (w + .03, d + .03, .5), (0, 0, .5), toalha, col, r)
        box(nome + "_Toalha_Topo", (w + .03, d + .03, .012), (0, 0, .75), toalha, col, r)
    return r
def giroflex(R, col, x, z, larg=1.1):
    box("Giroflex_Base", (.32, larg, .05), (x, 0, z), M["preto"], col, R, bevel=.015)
    n = 6; w = larg / n
    for k in range(n):
        y = -larg / 2 + w * (k + .5)
        box("Giroflex_Lente_%d" % (k + 1), (.28, w * .92, .09), (x, y, z + .07), M["giro_verm"] if k < 3 else M["giro_azul"], col, R, bevel=.022)
    luz("Giroflex_Luz_Vermelha", "POINT", 0, "#ff1a10", (x, -.35, z + .2), col, R)
    luz("Giroflex_Luz_Azul", "POINT", 0, "#2050ff", (x, .35, z + .2), col, R)

CARROS = os.path.join(AQUI, "modelos", "carros")

def repintar(img, cor, nome):
    """Troca a cor da pintura (pixels saturados da textura) mantendo sombras, frisos e detalhes."""
    w, h = img.size; px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(-1, 4)
    rgb = px[:, :3]; mx = rgb.max(1); mn = rgb.min(1); sat = (mx - mn) / np.maximum(mx, 1e-4)
    m = (sat > .3) & (mx > .12)
    if m.sum() < 100: return img
    ref = np.median(mx[m]); k = np.clip(mx[m] / ref, 0, 1.6)[:, None]
    rgb[m] = np.clip(np.array(lin(hx(cor)) if False else hx(cor), np.float32)[None, :] * k, 0, 1)
    novo = bpy.data.images.new(nome, w, h, alpha=True); novo.pixels.foreach_set(px.ravel()); novo.pack()
    return novo

M["int_forro"] = mat("Interior_Forro", "#1d1f22", .9)      # forro interno do carro abordado

def carro_modelo(nome, col, arquivo, pos, rz, cor=None, tirar=(), janela_aberta=False, interior=False, porta=None, escala=1.0):
    """Importa modelos/carros/<arquivo>.glb com a frente para +X. Devolve (raiz, sup_y, sup_x, info) ou None se faltar."""
    caminho = os.path.join(CARROS, arquivo + ".glb")
    if not os.path.exists(caminho): return None
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=caminho)
    novos = [o for o in bpy.data.objects if o not in antes]
    R = next(o for o in novos if o.parent is None); R.name = nome
    for o in novos:
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
        if o is not R: o.name = nome + "_" + o.name.split(".")[0].replace("Roda_", "Roda_")
    if escala != 1.0:
        for o in novos:
            if o.type == "MESH":
                o.data.transform(Matrix.Scale(escala, 4)); o.location = o.location * escala
    corpo = next(o for o in novos if o.type == "MESH" and "Carroceria" in o.name)
    feitos = {}
    for i, s in enumerate(corpo.material_slots):          # materiais proprios deste carro (UV do modelo e preservada no pipeline)
        m = s.material.copy(); m.name = "Modelo_%s_%s" % (nome, s.material.name.split(".")[0]); s.material = m
        b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        tex = next((n for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.outputs["Color"].is_linked and any(l.to_socket.name == "Base Color" for l in n.outputs["Color"].links)), None)
        nm = m.name.lower()
        if cor and tex and tex.image and not any(k in nm for k in ("glass", "optic", "decal")):
            tex.image = feitos.setdefault(tex.image.name, repintar(tex.image, cor, "pintura_%s_%s" % (nome, tex.image.name)))
        if "glass" in nm and b:
            for l in list(b.inputs["Alpha"].links): m.node_tree.links.remove(l)
            for l in list(b.inputs["Base Color"].links): m.node_tree.links.remove(l)
            b.inputs["Base Color"].default_value = (.03, .045, .055, 1); b.inputs["Alpha"].default_value = .38 if interior else .8
            b.inputs["Roughness"].default_value = .06; b.inputs["Metallic"].default_value = 0
            for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
                try: setattr(m, attr, val)
                except Exception: pass
        if interior: m.use_backface_culling = "glass" not in nm      # lataria so por fora: por dentro entra o forro (abaixo)
    for o in novos:                                       # rodas: mesmo prefixo "Modelo_", senao o pipeline refaz a UV e embaralha a textura
        if o.type == "MESH" and o is not corpo:
            for s in o.material_slots:
                if s.material and not s.material.name.startswith("Modelo_"):
                    m = s.material.copy(); m.name = "Modelo_%s_%s" % (nome, s.material.name.split(".")[0]); s.material = m
    me = corpo.data
    bm = bmesh.new(); bm.from_mesh(me)
    nomes = [s.material.name.lower() for s in corpo.material_slots]
    apagar = [f for f in bm.faces if any(k in nomes[f.material_index] for k in tirar)]
    vidro = [f for f in bm.faces if "glass" in nomes[f.material_index]]
    esq = [f for f in vidro if f.normal.y > .55 and abs(f.normal.z) < .6]          # vidros laterais do lado do motorista (+Y)
    info = {}
    if esq:
        xs = [f.calc_center_median().x for f in esq]; meio = (min(xs) + max(xs)) / 2
        frente = [f for f in esq if f.calc_center_median().x > meio]
        c = sum((f.calc_center_median() for f in frente), Vector()) / len(frente)
        info["janela"] = c.copy()
        info["jx"] = (min(v.co.x for f in frente for v in f.verts), max(v.co.x for f in frente for v in f.verts))
        if interior:
            # o modelo traz uma "tampa" preta horizontal dentro da cabine, na altura da base das janelas, para esconder o
            # interior vazio. Com condutor e bancos la dentro ela corta o personagem no peito: sai.
            hw_c = max(v.co.y for v in bm.verts)
            for f in bm.faces:
                cf = f.calc_center_median()
                if "glass" not in nomes[f.material_index] and f.normal.z > .7 and min(xs) - .3 < cf.x < max(xs) + .12 and abs(cf.y) < hw_c * .8 and c.z - .38 < cf.z < c.z - .05:
                    apagar.append(f)
        if janela_aberta: apagar += frente
    if apagar: bmesh.ops.delete(bm, geom=list(set(apagar)), context="FACES")
    if interior:
        # forro interno: uma copia da lataria, 2 cm para dentro e virada para o interior, em material escuro.
        # Sem isso via-se a pintura do carro pelo lado de dentro (portas, colunas e teto). Como acompanha a lataria
        # por dentro, nunca aparece do lado de fora.
        mi = len(me.materials); me.materials.append(M["int_forro"]); nomes.append("int_forro")
        dup = bmesh.ops.duplicate(bm, geom=[f for f in bm.faces if "glass" not in nomes[f.material_index]])
        nf = [g for g in dup["geom"] if isinstance(g, bmesh.types.BMFace)]
        bm.normal_update()
        for v in {v for f in nf for v in f.verts}: v.co -= v.normal * .02
        bmesh.ops.reverse_faces(bm, faces=nf)
        for f in nf: f.material_index = mi
    tem_porta = False
    if porta and "jx" in info:
        # porta do motorista: recorta a lateral esquerda entre a coluna da frente e a do meio, da soleira ao teto,
        # e separa numa peca propria com a origem na dobradica (o site gira a peca para abrir)
        hw_ = max(v.co.y for v in bm.verts)
        xd1, zb_ = info["jx"][1] + porta[1], porta[2]; xd0 = xd1 - porta[0]       # porta = (comprimento, folga a frente da janela, altura da soleira)
        for co, no in (((xd0, 0, 0), (1, 0, 0)), ((xd1, 0, 0), (1, 0, 0)), ((0, 0, zb_), (0, 0, 1))):
            fs = [f for f in bm.faces if f.calc_center_median().y > 0]
            geom = list({v for f in fs for v in f.verts}) + list({e for f in fs for e in f.edges}) + fs
            bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, dist=1e-4)
        for f in bm.faces:
            c = f.calc_center_median()
            f.select = bool(c.y > hw_ * .45 and xd0 < c.x < xd1 and c.z > zb_ and abs(f.normal.z) < .8)      # lataria e forro da porta
        tem_porta = any(f.select for f in bm.faces)
        info["dobradica"] = Vector((xd1, hw_ - .04, zb_ + .35))
    bm.to_mesh(me); bm.free()
    if tem_porta:
        mp = me.copy(); mp.name = nome + "_Porta"
        for malha_, manter_sel in ((me, False), (mp, True)):
            b2 = bmesh.new(); b2.from_mesh(malha_)
            bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.select != manter_sel], context="FACES")
            if manter_sel: bmesh.ops.translate(b2, verts=b2.verts, vec=-info["dobradica"])
            b2.to_mesh(malha_); b2.free()
        P = bpy.data.objects.new(nome + "_Porta", mp); col.objects.link(P); P.parent = R; P.location = info["dobradica"]
        for p_ in mp.polygons: p_.use_smooth = True
    R.location = pos; R.rotation_euler = (0, 0, rz)
    bpy.context.view_layer.update()
    pts = [Vector(c) for c in corpo.bound_box]
    hw = max(abs(p.y) for p in pts); comp = max(p.x for p in pts) - min(p.x for p in pts); alt = max(p.z for p in pts)
    info.update(hw=hw, comp=comp, alt=alt)
    if interior and "janela" in info:                     # o modelo e oco: bancos, painel e assoalho simples
        j = info["janela"]; xb = j.x - .18; zb = j.z - .62; yb = hw * .45
        for sy in (-1, 1):
            box(nome + "_Banco", (.5, .48, .1), (xb, sy * yb, zb), M["interior"], col, R, bevel=.04)
            box(nome + "_Encosto", (.12, .46, .6), (xb - .3, sy * yb, zb + .34), M["interior"], col, R, rot=(0, .2, 0), bevel=.04)
        box(nome + "_Banco_Tras", (.5, hw * 1.5, .1), (xb - .95, 0, zb + .02), M["interior"], col, R, bevel=.04)
        box(nome + "_Encosto_Tras", (.12, hw * 1.5, .5), (xb - 1.22, 0, zb + .32), M["interior"], col, R, rot=(0, .2, 0), bevel=.04)
        box(nome + "_Painel", (.3, hw * 1.55, .22), (xb + .8, 0, zb + .21), M["interior"], col, R, bevel=.05)      # topo abaixo do peitoril: nao tapa o condutor
        # volante: aro (anel), cubo e tres raios. Um disco cheio tapava o peito e os bracos do condutor
        _vp, _vr = (xb + .52, yb, zb + .39), (0, -1.15, 0)
        torno(nome + "_Volante", [(.17 + .013 * math.cos(2 * PI * k / 8), .013 * math.sin(2 * PI * k / 8)) for k in range(9)], M["preto"], col, R, pos=_vp, rot=_vr, seg=24)
        cyl(nome + "_Volante_Cubo", .045, .045, .03, _vp, M["preto"], col, R, rot=_vr, seg=12)
        for _a in (PI / 2, PI * 7 / 6, PI * 11 / 6):
            _b = box(nome + "_Volante_Raio", (.15, .028, .012), _vp, M["preto"], col, R, rot=_vr)
            _b.rotation_euler = (Matrix.Rotation(-1.15, 4, "Y") @ Matrix.Rotation(_a, 4, "Z")).to_euler()
            _b.location = Vector(_vp) + (Matrix.Rotation(-1.15, 4, "Y") @ Matrix.Rotation(_a, 4, "Z")) @ Vector((.095, 0, 0))
        box(nome + "_Assoalho", (comp * .62, hw * 1.5, .03), (xb - .2, 0, zb - .28), M["preto"], col, R)
        info["banco"] = [xb, yb, zb + .05]
    ev = corpo.evaluated_get(bpy.context.evaluated_depsgraph_get())
    def sup_y(x, z, lado):
        ok, lc, _, _ = ev.ray_cast(Vector((x, lado * 3.0, z)), Vector((0, -lado, 0)))
        return lc.y if ok else lado * hw
    def sup_x(y, z, ponta):
        ok, lc, _, _ = ev.ray_cast(Vector((ponta * 6.0, y, z)), Vector((-ponta, 0, 0)))
        return lc.x if ok else ponta * comp / 2
    return R, sup_y, sup_x, info

def faixa_lateral(nome, R, col, sup_y, x0, x1, z0, z1, m, n=24):
    """Faixa pintada que acompanha a lateral do carro (dos dois lados)."""
    for lado in (1, -1):
        vs, fs = [], []
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            for z in (z0, z1): vs.append((x, sup_y(x, z, lado) + lado * .006, z))
        for i in range(n): fs.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
        malha(nome, vs, fs, m, col, R)

# ================================================================== CASSINO CLANDESTINO
# Planta (metros). A rua corre em X; o predio fica do lado +Y da calcada.
#   rua            y -9 .. -2      calcada  y -2 .. 0
#   bar (fachada)  x -6 .. 6,  y 0 .. 6      aberto ao publico; entrada x -3 .. -1
#   corredor       x -6 .. -3.5, y 6 .. 8.5  porta "PRIVATIVO" no fundo do bar
#   deposito de maquinas  x -6 .. -3.5, y 8.5 .. 13
#   SALAO DE JOGOS x -3.5 .. 2.5, y 6 .. 13  caca-niqueis, carteado, roleta; porta dos fundos
#   deposito do bar x 2.5 .. 6, y 6 .. 9
#   escritorio/caixa x 2.5 .. 6, y 9 .. 13   porta trancada e guiche
#   quintal        x -6 .. 6, y 13 .. 17     portao para o beco
#   beco           x -8 .. -6, y 0 .. 17     sai na rua
FZ = .15                       # nivel do piso interno e da calcada
PD = 3.0                       # pe-direito
DIR_U = {"-y": (1, 0, 0), "+y": (-1, 0, 0), "-x": (0, -1, 0), "+x": (0, 1, 0)}

def tex_ceramica(cor, rejunte="#8d8a84", S=256, n=4):
    r = np.random.default_rng(int(sum(cor) * 1000)); cel = S // n
    a = np.kron(r.uniform(.9, 1.05, (n, n, 1)), np.ones((cel, cel, 1))) * np.array(cor)
    a *= (1 + .03 * r.standard_normal((S, S, 1)))
    yy, xx = np.mgrid[0:S, 0:S]
    a[(xx % cel < 2) | (yy % cel < 2)] = np.array(hx(rejunte))
    return np.clip(a, 0, 1)

def tex_caca_niquel(seed, S=128):
    """Tela de tres rolos com figuras geometricas coloridas (desenho proprio, sem marcas)."""
    a = np.zeros((S, S, 3)); a[:] = hx("#0b0f1e")
    r = np.random.default_rng(seed); cores = [hx(c) for c in ("#ff3b30", "#ffd60a", "#34c759", "#0a84ff", "#ff9f0a", "#bf5af2")]
    yy, xx = np.mgrid[0:S, 0:S]
    for i in range(3):
        for j in range(3):
            cx, cy = 22 + i * 42, 22 + j * 42; c = np.array(cores[r.integers(6)]); f = r.integers(3)
            m = ((xx - cx) ** 2 + (yy - cy) ** 2 < 196) if f == 0 else ((abs(xx - cx) + abs(yy - cy)) < 17) if f == 1 else ((abs(xx - cx) < 12) & (abs(yy - cy) < 12))
            a[m] = c * (1 if j == 1 else .4)
    a[(xx % 42 < 2)] = .22
    a[abs(yy - 64) < 1] = (1, 1, 1)
    return a

def tex_cameras(S=128):
    """Monitor das cameras de seguranca: quatro quadros cinzentos."""
    r = np.random.default_rng(3); a = np.zeros((S, S, 3)); h = S // 2
    for i in range(2):
        for j in range(2):
            g = r.uniform(.12, .4); q = np.ones((h, h, 3)) * g
            q[r.integers(10, 40):r.integers(42, 60), r.integers(8, 30):r.integers(34, 60)] = g * r.uniform(.3, 1.8)
            a[j * h:(j + 1) * h, i * h:(i + 1) * h] = q
    a[h - 1:h + 1, :] = 0; a[:, h - 1:h + 1] = 0
    return np.clip(a * np.array((.8, 1, .9)), 0, 1)

def tela_mat(nome, img, forca=2.5):
    """Material de tela acesa com imagem (UV propria: o nome comeca com Img_ e o pipeline preserva a UV)."""
    m = bpy.data.materials.new("Img_" + nome); nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = forca; b.inputs["Roughness"].default_value = .25
    return m

def quadro(name, centro, virado, larg, alt, m, col, parent=None):
    """Retangulo vertical com UV de 0 a 1 (telas), legivel de quem esta do lado 'virado'."""
    du = Vector(DIR_U[virado]); c = Vector(centro)
    return adesivo(name, lambda u, v: c + du * (u - .5) * larg + Vector((0, 0, (v - .5) * alt)), 1, 1, col, parent, mat=m)

M.update({
    "parede": mat("Reboco_Interno", "#d6ccb2", .92), "fach": mat("Fachada_Bar", "#c79a3e", .9),
    "piso_bar": img_mat("Piso_Ceramica", np_image("piso_ceramica", tex_ceramica(hx("#b9a98c"))), 1.2, .45),
    "azulejo": img_mat("Azulejo_Branco", np_image("azulejo_branco", tex_ceramica(hx("#e4e2da"), "#a5a39c", n=8)), 1.2, .2),
    "carpete": mat("Piso_Taco_Salao", "#8a6a48", .5), "cortina_br": mat("Cortina_Branca", "#d9d6cc", .95), "cimento": mat("Piso_Cimento", "#77746e", .85),
    "laje": mat("Laje_Teto", "#cbc6ba", .95), "muro": mat("Muro_Reboco", "#a8a296", .95),
    "mad": mat("Madeira_Balcao", "#5a3a26", .5), "mad_cl": mat("Madeira_Clara", "#9a7650", .6),
    "porta_mad": mat("Porta_Madeira", "#6b4a30", .6), "porta_ferro": mat("Porta_Ferro", "#4a4f55", .5, .6),
    "feltro": mat("Feltro_Verde", "#1f6b3a", .98), "couro": mat("Couro_Vinho", "#5a1c1c", .55),
    "gab": mat("Gabinete_Maquina", "#1b1d2a", .4), "gab2": mat("Gabinete_Detalhe", "#7a1620", .35),
    "neon_r": mat("Neon_Vermelho", "#40080a", .3, emit="#ff2a2a", forca=6), "neon_v": mat("Neon_Verde", "#06301a", .3, emit="#2aff7a", forca=5),
    "neon_a": mat("Neon_Ambar", "#402a05", .3, emit="#ffb020", forca=6), "neon_az": mat("Neon_Azul", "#06123a", .3, emit="#3a7bff", forca=6),
    "lamp_q": mat("Lampada_Quente", "#ffffff", .4, emit="#ffd9a0", forca=18), "lamp_f": mat("Lampada_Fria", "#ffffff", .4, emit="#eaf2ff", forca=14),
    "garrafa_v": mat("Garrafa_Verde", "#1f4a2a", .1), "garrafa_a": mat("Garrafa_Ambar", "#5a3410", .1), "garrafa_c": mat("Garrafa_Clara", "#b9c4c4", .08),
    "eng_v": mat("Engradado_Vermelho", "#b8231c", .6), "eng_a": mat("Engradado_Amarelo", "#d9a514", .6),
    "freezer": mat("Freezer_Branco", "#e8e8e4", .35), "papelao": mat("Caixa_Papelao", "#a9825a", .9),
    "nota": mat("Dinheiro_Notas", "#6f9a7a", .8), "nota2": mat("Dinheiro_Notas_Azul", "#5d86a8", .8), "elastico": mat("Elastico", "#b3261e", .7),
    "ficha_r": mat("Ficha_Vermelha", "#c0261e", .4), "ficha_a": mat("Ficha_Azul", "#1e4fb8", .4), "ficha_p": mat("Ficha_Preta", "#161616", .4), "ficha_b": mat("Ficha_Branca", "#ecebe6", .4),
    "cofre": mat("Cofre_Aco", "#3a3d42", .4, .7), "tv": mat("Tela_TV", "#000000", .2, emit="#8fb4ff", forca=1.8),
    "capa": mat("Caderno_Capa", "#1c2a52", .7), "dourado": mat("Metal_Dourado", "#b08d3c", .3, .9),
})
TELAS = [tela_mat("Tela_Caca_Niquel_%d" % i, np_image("tela_caca_niquel_%d" % i, tex_caca_niquel(11 + i))) for i in range(4)]
TELA_CAM = tela_mat("Monitor_Cameras", np_image("monitor_cameras", tex_cameras()), 1.6)
C_RUA = collection("01_Rua"); C_PRED = collection("02_Vizinhos"); C_EST = collection("03_Bar_Estrutura")
C_BAR = collection("04_Bar_Moveis"); C_SAL = collection("05_Salao_Jogos"); C_ESC = collection("06_Escritorio_Depositos")
C_FUN = collection("07_Fundos_Beco"); C_INT = collection("08_Interativos"); C_LUZ = collection("09_Luzes_Cameras")
C_VEIC = collection("10_Viatura")
C_VEG = C_RUA; C_BLITZ = C_BAR

def parede(nome, a, b, m, col, vaos=(), h=PD, t=.2, z0=FZ, ext=None):
    """Parede reta entre a=(x, y) e b=(x, y), alinhada a um eixo, com vaos [(d0, d1, zbase, ztopo)] medidos a partir de a.
    Cada trecho e uma caixa separada: a malha de colisao usa uma caixa por objeto, entao os vaos ficam livres."""
    ax, ay = a; bx, by = b; horiz = abs(bx - ax) > abs(by - ay)
    L = abs(bx - ax) if horiz else abs(by - ay); sg = 1 if ((bx - ax) if horiz else (by - ay)) > 0 else -1
    def trecho(d0, d1, zb, zt, suf):
        if d1 - d0 < .01 or zt - zb < .01: return
        c = (d0 + d1) / 2
        pos = (ax + sg * c, ay, z0 + (zb + zt) / 2) if horiz else (ax, ay + sg * c, z0 + (zb + zt) / 2)
        box(nome + suf, (d1 - d0, t, zt - zb) if horiz else (t, d1 - d0, zt - zb), pos, m, col)
    if ext is None: ext = t / 2 if t >= .2 else -.07      # paredes internas param 3 cm dentro da parede vizinha (sem faces coincidentes)
    d = -ext
    for v0, v1, zb, zt in sorted(vaos):
        trecho(d, v0, 0, h, ""); trecho(v0, v1, 0, zb, "_Mureta"); trecho(v0, v1, zt, h, "_Verga"); d = v1
    trecho(d, L + ext, 0, h, "")

def ponto(nome, x, y, olha=(0, -1), z=FZ):
    """Ponto usado pelo site (personagens, maquinas, rotas): vazio P_<nome>; rz = para onde a pessoa olha."""
    return vazio("P_" + nome, (x, y, z), C_LUZ, math.atan2(olha[0], -olha[1]))

# ------------------------------------------------------------------ 1. rua, calcadas, beco
RUA_X = 30.0
box("Asfalto", (2 * RUA_X, 7, .2), (0, -5.5, -.1), M["asfalto"], C_RUA)
for yc, larg in ((-1.0, 2.0), (-10.0, 2.0)):
    box("Calcada", (2 * RUA_X, larg, FZ), (0, yc, FZ / 2), M["calcada"], C_RUA)
for y in (-2.09, -8.91):
    box("Meio_Fio", (2 * RUA_X, .18, .3), (0, y, 0), M["meiofio"], C_RUA, bevel=.02)
x = -RUA_X + 1
while x < RUA_X - 2:
    box("Faixa_Tracejada", (2.0, .12, .004), (x + 1, -5.5, .003), M["faixa_am"], C_RUA); x += 6.0
for x in (-17, 12):
    cyl("Tampa_Bueiro", .32, .32, .01, (x, -4.2, .004), M["loja"], C_RUA, seg=24)
for i, x in enumerate((-16, 9, 27)):
    poste("Poste_%d" % i, x, -1.75, 1)

# vizinhos: dos dois lados do bar (depois do beco) e do outro lado da rua
cores = [M["reboco_a"], M["pastilha_a"], M["reboco_c"], M["reboco_d"], M["reboco_b"], M["pastilha_b"]]
for i, (x0, x1, and_) in enumerate(((-30, -19, 4), (-19, -8.1, 2), (6.1, 17, 3), (17, 30, 5))):
    predio("Predio_N_%d" % i, x0 + .1, x1 - .1, 0.0, 1, 4.2 + and_ * 3.0, cores[(i * 5 + 2) % 6], and_, i % 4)
x = -RUA_X; i = 0
while x < RUA_X - 1:
    w = min(rnd.choice((12, 15, 18)), RUA_X - x); and_ = rnd.choice((2, 3, 4, 5))
    predio("Predio_S_%d" % i, x + .1, x + w - .1, -11.0, -1, 4.2 + and_ * 3.0, cores[(i * 5) % 6], and_, (i + 1) % 4)
    x += w; i += 1

# ------------------------------------------------------------------ 2. estrutura do predio
box("Piso_Bar", (12, 6, FZ), (0, 3, FZ / 2), M["piso_bar"], C_EST)
box("Piso_Salao", (6, 7, FZ), (-.5, 9.5, FZ / 2), M["carpete"], C_EST)
box("Piso_Corredor", (2.5, 7, FZ), (-4.75, 9.5, FZ / 2), M["cimento"], C_EST)
box("Piso_Escritorio", (3.5, 7, FZ), (4.25, 9.5, FZ / 2), M["cimento"], C_EST)
box("Laje", (12.2, 13.2, .2), (0, 6.5, FZ + PD + .1), M["laje"], C_EST)
# paredes externas
parede("Parede_Fachada", (-6, 0), (6, 0), M["fach"], C_EST, vaos=[(3.0, 5.0, 0, 2.6)])          # entrada do bar: x -3 .. -1
parede("Parede_Oeste", (-6, 0), (-6, 13), M["parede"], C_EST)
parede("Parede_Leste", (6, 0), (6, 13), M["parede"], C_EST)
parede("Parede_Fundo", (-6, 13), (6, 13), M["parede"], C_EST, vaos=[(7.4, 8.3, 0, 2.1)])          # porta dos fundos: x 1.4 .. 2.3
# paredes internas
parede("Parede_Bar_Fundo", (-6, 6), (6, 6), M["parede"], C_EST, t=.15,
       vaos=[(.8, 1.7, 0, 2.1), (10.4, 11.2, 0, 2.1)])                                            # porta PRIVATIVO x -5.2 .. -4.3; deposito do bar x 4.4 .. 5.2
parede("Parede_Corredor", (-3.5, 6), (-3.5, 13), M["parede"], C_EST, t=.15, vaos=[(.6, 1.8, 0, 2.1)])   # vao do corredor para o salao
parede("Parede_Dep_Maquinas", (-6, 8.5), (-3.5, 8.5), M["parede"], C_EST, t=.15, vaos=[(.8, 1.6, 0, 2.1)])
parede("Parede_Salao_Leste", (2.5, 6), (2.5, 13), M["parede"], C_EST, t=.15,
       vaos=[(3.4, 4.3, 0, 2.1), (5.0, 6.0, 1.05, 1.65)])                                         # porta do escritorio y 9.4 .. 10.3; guiche y 11 .. 12
parede("Parede_Escritorio_Sul", (2.5, 9), (6, 9), M["parede"], C_EST, t=.15)
# segundo andar (sobrado) e fachada
box("Sobrado_Andar", (12.2, 13.2, 3.1), (0, 6.5, FZ + PD + .2 + 1.55), M["fach"], C_PRED)
for i, x in enumerate((-4, 0, 4)):
    box("Sobrado_Moldura", (1.54, .1, 1.44), (x, -.12, 5.1), M["esquadria"], C_PRED)
    box("Sobrado_Janela", (1.4, .03, 1.3), (x, -.17, 5.1), M["cortina"] if i == 1 else M["janela_off"], C_PRED)
box("Sobrado_Cornija", (12.4, .4, .2), (0, -.1, 6.55), M["concreto"], C_PRED)
box("Bar_Marquise", (12, 1.1, .12), (0, -.55, 3.3), M["concreto"], C_PRED)
box("Bar_Letreiro_Fundo", (5.0, .06, .7), (-2, -.14, 3.75), LETREIROS[0], C_PRED)
texto("Bar_Letreiro_Texto", "BAR E PETISCOS", .34, (-2, -.18, 3.75), "-y", M["texto_letreiro"], C_PRED)
box("Bar_Porta_Enrolada", (2.1, .3, .3), (-2, .05, FZ + 2.75), M["porta_enrolar"], C_EST)        # porta de enrolar aberta (recolhida)
box("Bar_Porta_Loja_Fechada", (3.0, .06, 2.7), (2.6, -.13, FZ + 1.35), M["porta_enrolar"], C_PRED)   # segunda porta, sempre fechada
box("Bar_Rodape_Fachada", (12, .05, .5), (0, -.125, FZ + .25), M["rodape"], C_PRED)
for x, y in ((-5.8, 5.7), (0, 12.7), (5.7, 5.7)):                                                 # cameras de seguranca (cupulas)
    cyl("Camera_Seguranca", .07, .05, .07, (x * .97, y, FZ + PD - .04), M["preto_b"], C_EST, seg=12)

# ------------------------------------------------------------------ 3. bar
box("Balcao_Corpo", (.6, 3.6, 1.05), (3.6, 3.0, FZ + .525), M["mad"], C_BAR, bevel=.01)
box("Balcao_Tampo", (.75, 3.75, .05), (3.55, 3.0, FZ + 1.075), M["rodape"], C_BAR, bevel=.012)
box("Balcao_Retorno", (2.4, .5, 1.05), (4.8, 1.1, FZ + .525), M["mad"], C_BAR, bevel=.01)
for k in range(4):
    cyl("Banqueta_Assento", .17, .17, .05, (2.95, 1.9 + k * .75, FZ + .74), M["couro"], C_BAR, seg=16)
    cyl("Banqueta_Pe", .14, .03, .72, (2.95, 1.9 + k * .75, FZ + .36), M["metal"], C_BAR, seg=10)
for k, z in enumerate((1.0, 1.45, 1.9)):                                                          # prateleiras de garrafas na parede leste
    box("Prateleira_Bar", (.26, 3.2, .035), (5.76, 3.4, FZ + z), M["mad_cl"], C_BAR)
    for j in range(12):
        g = M[("garrafa_v", "garrafa_a", "garrafa_c")[(j + k) % 3]]; y = 1.95 + j * .26
        torno("Garrafa", [(0, 0), (.036, 0), (.036, .17), (.013, .23), (.013, .29), (0, .29)], g, C_BAR, pos=(5.76, y, FZ + z + .018), seg=10)
box("Freezer_Horizontal", (.7, 1.5, .9), (5.5, 5.1, FZ + .45), M["freezer"], C_BAR, bevel=.03)
box("Geladeira_Vertical", (.7, .7, 1.9), (5.5, 1.75, FZ + .95), M["freezer"], C_BAR, bevel=.03)
box("TV_Bar", (1.1, .06, .64), (0.5, 5.86, FZ + 2.2), M["preto_b"], C_BAR, bevel=.01)
box("TV_Bar_Tela", (1.02, .01, .56), (0.5, 5.82, FZ + 2.2), M["tv"], C_BAR)
box("Azulejo_Barra", (9.4, .02, 1.3), (-.9, 5.91, FZ + .65), M["azulejo"], C_BAR)
for i, (x, y, rz) in enumerate(((-.2, 2.0, .2), (-3.9, 2.2, -.15), (0.6, 4.4, .05))):
    r = mesa("Mesa_Bar_%d" % i, x, y, rz, tam=(.75, .75), col=C_BAR); r.location.z = FZ
    for k, (dx, dy, a) in enumerate(((0, -.62, PI), (0, .62, 0), (-.62, 0, -PI / 2), (.62, 0, PI / 2))[:3 + (i % 2)]):
        c = cadeira("Cadeira_Bar_%d_%d" % (i, k), x + dx, y + dy, rz + a + rnd.uniform(-.2, .2), C_BAR); c.location.z = FZ
    torno("Garrafa_Mesa", [(0, 0), (.036, 0), (.036, .17), (.013, .23), (.013, .29), (0, .29)], M["garrafa_a"], C_BAR, pos=(x + .1, y + .05, FZ + .745), seg=10)
    cyl("Copo_Mesa", .03, .025, .1, (x - .12, y - .1, FZ + .795), M["garrafa_c"], C_BAR, seg=10)
for k in range(3):                                                                                # deposito do bar
    for j in range(2 + k % 2):
        box("Engradado", (.4, .3, .28), (5.6, 6.5 + k * .45, FZ + .14 + j * .285), M["eng_v"] if (k + j) % 2 else M["eng_a"], C_ESC, bevel=.01)
box("Estante_Deposito", (.45, 2.2, 1.9), (2.85, 7.6, FZ + .95), M["poste"], C_ESC)
for k in range(5):
    box("Caixa_Bebida", (.38, .38, .3), (2.85, 6.8 + k * .42, FZ + 1.95 + .15), M["papelao"], C_ESC)

# ------------------------------------------------------------------ 4. salao de jogos
def maquina(i, x, y, olha, col=C_SAL, ligada=True):
    """Caca-niquel de gabinete, no formato comum nas apreensoes (desenho proprio, sem marcas): gabinete preto com
    frisos cromados, topo em arco iluminado, tela, noteiro a direita, mesa de botoes inclinada e bandeja de moedas."""
    n = "Caca_Niquel_%02d" % i; rz = math.atan2(olha[0], -olha[1]); r = vazio(n, (x, y, FZ), col, rz)
    box(n + "_Gabinete", (.6, .55, 1.42), (0, 0, .71), M["gab"], col, r, bevel=.02)
    for sx in (-1, 1):
        box(n + "_Friso", (.022, .03, 1.4), (sx * .295, -.268, .7), M["cromo"], col, r)
    box(n + "_Mesa_Botoes", (.6, .27, .07), (0, -.38, .84), M["gab"], col, r, rot=(.3, 0, 0), bevel=.012)
    box(n + "_Bandeja", (.2, .1, .035), (.12, -.33, .6), M["cromo"], col, r)
    box(n + "_Porta_Cofre", (.5, .012, .46), (0, -.277, .3), M["plast"], col, r)
    box(n + "_Noteiro", (.11, .014, .26), (.2, -.279, 1.14), M["plast"], col, r)
    cyl(n + "_Topo_Arco", .3, .3, .16, (0, -.14, 1.42), M["gab"], col, r, rot=(PI / 2, 0, 0), seg=28)
    if ligada:
        quadro(n + "_Tela", (-.075, -.279, 1.14), "-y", .38, .32, TELAS[i % 4], col, r)
        box(n + "_Noteiro_Luz", (.07, .006, .016), (.2, -.288, 1.1), M["neon_v"], col, r)
        cyl(n + "_Topo_Luz", .27, .27, .012, (0, -.226, 1.42), (M["neon_az"], M["neon_a"], M["neon_r"], M["neon_v"])[i % 4], col, r, rot=(PI / 2, 0, 0), seg=28)
        texto(n + "_Topo_Texto", ("DIVIRTA-SE", "BOA SORTE", "PRÊMIOS", "JOGUE AQUI")[i % 4], .058, (0, -.236, 1.53), "-y", M["texto_br"], col, r)
        for k in range(10):
            box(n + "_Botao", (.036, .036, .014), (-.2 + (k % 5) * .075, -.42 + (k // 5) * .07, .845 + (k // 5) * .022), M["branco"] if k % 3 else M["neon_a"], col, r, rot=(.3, 0, 0))
        # cadeira de escritorio na frente
        box(n + "_Cadeira_Assento", (.46, .44, .07), (0, -.95, .47), M["preto"], col, r, bevel=.03)
        box(n + "_Cadeira_Encosto", (.42, .06, .46), (0, -1.17, .82), M["preto"], col, r, rot=(.12, 0, 0), bevel=.03)
        cyl(n + "_Cadeira_Coluna", .025, .025, .4, (0, -.95, .24), M["metal"], col, r, seg=8)
        cyl(n + "_Cadeira_Base", .27, .27, .04, (0, -.95, .03), M["plast"], col, r, seg=5)
        ponto("Maquina_%02d" % i, x, y, olha)
    else:
        box(n + "_Tela_Apagada", (.38, .012, .32), (-.075, -.277, 1.14), M["preto_b"], col, r)
    return r

MAQUINAS = [(-2.9 + k * .8, 12.6, (0, -1)) for k in range(5)] + [(-3.1, 9.0 + k * .9, (1, 0)) for k in range(3)]
for i, (x, y, o) in enumerate(MAQUINAS):
    maquina(i + 1, x, y, o)
# mesa de carteado (redonda, feltro verde)
CX, CY = 0.4, 7.9
cyl("Mesa_Carteado_Pe", .09, .3, .72, (CX, CY, FZ + .36), M["mad"], C_SAL, seg=12)
cyl("Mesa_Carteado_Borda", .7, .7, .06, (CX, CY, FZ + .75), M["mad"], C_SAL, seg=28)
cyl("Mesa_Carteado_Feltro", .62, .62, .012, (CX, CY, FZ + .785), M["feltro"], C_SAL, seg=28)
for k in range(4):
    a = PI / 4 + k * PI / 2; x, y = CX + 1.02 * math.cos(a), CY + 1.02 * math.sin(a)
    box("Cadeira_Jogo_Assento", (.44, .44, .08), (x, y, FZ + .46), M["couro"], C_SAL, rot=(0, 0, a), bevel=.02)
    box("Cadeira_Jogo_Encosto", (.06, .44, .5), (x + .2 * math.cos(a), y + .2 * math.sin(a), FZ + .75), M["couro"], C_SAL, rot=(0, 0, a), bevel=.02)
    box("Cadeira_Jogo_Base", (.36, .36, .42), (x, y, FZ + .21), M["mad"], C_SAL, rot=(0, 0, a))
for k in range(9):                                                                                # cartas na mesa
    a = rnd.uniform(0, 2 * PI); d = rnd.uniform(.05, .32)
    box("Carta", (.063, .088, .001), (CX + d * math.cos(a), CY + d * math.sin(a), FZ + .793 + k * .0006), M["papel"], C_SAL, rot=(0, 0, rnd.uniform(0, 3)))
# mesa de roleta
RX, RY = 0.3, 10.6
box("Mesa_Roleta_Corpo", (1.2, 2.3, .78), (RX, RY, FZ + .39), M["mad"], C_SAL, bevel=.02)
box("Mesa_Roleta_Feltro", (1.06, 2.16, .012), (RX, RY, FZ + .787), M["feltro"], C_SAL)
torno("Roleta_Bacia", [(0, .01), (.3, .01), (.4, .09), (.43, .09), (.43, 0), (0, 0)], M["mad_cl"], C_SAL, pos=(RX, RY + .65, FZ + .79), seg=32)
torno("Roleta_Disco", [(0, .045), (.05, .045), (.29, .025), (.29, .012), (0, .012)], M["preto_b"], C_SAL, pos=(RX, RY + .65, FZ + .79), seg=32)
cyl("Roleta_Eixo", .025, .012, .12, (RX, RY + .65, FZ + .89), M["dourado"], C_SAL, seg=12)
for k in range(18):
    a = 2 * PI * k / 18
    box("Roleta_Casa", (.07, .035, .004), (RX + .24 * math.cos(a), RY + .65 + .24 * math.sin(a), FZ + .818), M["ficha_r"] if k % 2 else M["ficha_b"], C_SAL, rot=(0, 0, a))
for i in range(3):                                                                                # quadro de apostas pintado no feltro
    for j in range(6):
        box("Roleta_Quadro", (.26, .2, .002), (RX - .28 + i * .28, RY - .95 + j * .22, FZ + .794), M["ficha_r"] if (i + j) % 2 else M["ficha_p"], C_SAL)
box("Cortina_Salao_Fundo", (4.6, .06, 2.7), (-1.1, 12.87, FZ + 1.5), M["cortina_br"], C_SAL)
box("Cortina_Salao_Oeste", (.06, 4.4, 2.7), (-3.39, 10.6, FZ + 1.5), M["cortina_br"], C_SAL)
box("Neon_Salao", (2.4, .04, .08), (-.5, 6.1, FZ + 2.5), M["neon_r"], C_SAL)
box("Neon_Salao_2", (.04, 2.0, .08), (2.4, 7.3, FZ + 2.5), M["neon_v"], C_SAL)
box("Bebedouro", (.34, .34, 1.0), (2.2, 6.35, FZ + .5), M["freezer"], C_SAL, bevel=.02)

# ------------------------------------------------------------------ 5. escritorio / caixa e deposito de maquinas
box("Guiche_Balcao", (.5, 1.1, .05), (2.6, 11.5, FZ + 1.05), M["mad_cl"], C_ESC)
for k in range(5):
    barra("Guiche_Grade", (2.5, 11.08 + k * .21, FZ + 1.07), (2.5, 11.08 + k * .21, FZ + 1.65), .008, M["poste"], C_ESC, seg=6)
box("Mesa_Escritorio_Tampo", (.75, 1.5, .04), (5.4, 11.2, FZ + .74), M["mad_cl"], C_ESC, bevel=.008)
box("Mesa_Escritorio_Gaveteiro", (.7, .45, .7), (5.4, 11.7, FZ + .35), M["mad_cl"], C_ESC)
box("Mesa_Escritorio_Lateral", (.7, .04, .72), (5.4, 10.47, FZ + .36), M["mad_cl"], C_ESC)
box("Cadeira_Escritorio_Assento", (.46, .46, .08), (4.7, 11.1, FZ + .46), M["preto"], C_ESC, bevel=.02)
box("Cadeira_Escritorio_Encosto", (.06, .44, .5), (4.5, 11.1, FZ + .78), M["preto"], C_ESC, bevel=.02)
cyl("Cadeira_Escritorio_Pe", .03, .22, .42, (4.7, 11.1, FZ + .21), M["metal"], C_ESC, seg=10)
box("Cofre", (.6, .55, .8), (5.6, 12.6, FZ + .4), M["cofre"], C_ESC, bevel=.02)
cyl("Cofre_Segredo", .06, .06, .03, (5.29, 12.6, FZ + .5), M["dourado"], C_ESC, rot=(0, PI / 2, 0), seg=16)
box("Estante_Escritorio", (1.6, .35, 1.8), (3.6, 12.75, FZ + .9), M["mad"], C_ESC)
box("Monitor_Cameras", (.5, .04, .32), (3.3, 12.55, FZ + 1.45), M["preto_b"], C_ESC)
quadro("Monitor_Cameras_Tela", (3.3, 12.527, FZ + 1.45), "-y", .46, .28, TELA_CAM, C_ESC)
box("Contadora_Notas", (.26, .22, .16), (5.45, 10.75, FZ + .84), M["branco"], C_ESC, bevel=.01)
for k in range(4):                                                                                # deposito: maquinas desligadas e caixas
    box("Caixa_Deposito", (.5, .5, .45), (-5.6, 9.0 + k * .55, FZ + .225 + (k % 2) * .0), M["papelao"], C_ESC)
maquina(21, -5.55, 12.3, (1, 0), C_ESC, ligada=False); maquina(22, -5.55, 11.5, (1, 0), C_ESC, ligada=False)
box("Placa_Maquina_Solta", (.5, .35, .03), (-4.3, 12.6, FZ + .3), M["plast"], C_ESC, rot=(1.1, 0, 0))

# ------------------------------------------------------------------ 6. quintal e beco
box("Piso_Quintal", (12, 4, FZ), (0, 15, FZ / 2), M["cimento"], C_FUN)
box("Piso_Beco", (2, 17, FZ), (-7, 8.5, FZ / 2), M["cimento"], C_FUN)
parede("Muro_Quintal_Fundo", (-8, 17), (6, 17), M["muro"], C_FUN, h=2.4)
parede("Muro_Quintal_Leste", (6, 13), (6, 17), M["muro"], C_FUN, h=2.4)
parede("Muro_Quintal_Oeste", (-6, 13), (-6, 17), M["muro"], C_FUN, h=2.4, vaos=[(1.6, 2.6, 0, 2.4)])   # portao do quintal para o beco
parede("Muro_Beco_Oeste", (-8, 0.1), (-8, 17), M["muro"], C_FUN, h=3.0, t=.1, ext=0)
box("Portao_Beco_Folha", (.05, 1.0, 2.0), (-6.05, 0.75, FZ + 1.0), M["porta_ferro"], C_FUN)     # portao do beco aberto, encostado na parede
box("Portao_Quintal_Folha", (.9, .05, 2.0), (-5.5, 15.55, FZ + 1.0), M["porta_ferro"], C_FUN)   # portao do quintal aberto
box("Tanque_Quintal", (.7, .55, .85), (5.5, 13.5, FZ + .425), M["concreto"], C_FUN)
for k in range(3):
    box("Engradado_Quintal", (.4, .3, .28), (3.6 + k * .45, 16.7, FZ + .14), M["eng_a"], C_FUN, bevel=.01)
cyl("Lixeira_Beco", .26, .22, .7, (-7.6, 3.0, FZ + .35), M["plast"], C_FUN, seg=14)
box("Maquina_Velha_Beco", (.62, .58, 1.2), (-7.55, 10.5, FZ + .6), M["gab"], C_FUN, rot=(0, .12, .3))

# ------------------------------------------------------------------ 7. interativos (portas e material a apreender)
def porta(nome, dobradica, rz, m, larg=.88, rotulo=None, lado_rotulo=-1):
    """Folha de porta com a origem na dobradica (o site gira a raiz para abrir). rz = 0: a folha corre para +X."""
    r = vazio(nome, (dobradica[0], dobradica[1], FZ), C_INT, rz)
    box(nome + "_Folha", (larg, .045, 2.08), (larg / 2, 0, 1.04), m, C_INT, r)
    for s in (-1, 1):
        cyl(nome + "_Macaneta", .025, .025, .05, (larg - .09, s * .05, 1.02), M["metal"], C_INT, r, rot=(PI / 2, 0, 0), seg=10)
    if rotulo:
        texto(nome + "_Rotulo", rotulo, .07, (larg / 2, lado_rotulo * .026, 1.62), "-y" if lado_rotulo < 0 else "+y", M["texto_br"], C_INT, r)
    return r
porta("I_Porta_Salao", (-5.2, 6.0), 0, M["porta_mad"], rotulo="PRIVATIVO")
porta("I_Porta_Escritorio", (2.5, 9.4), PI / 2, M["porta_mad"], rotulo="GERÊNCIA", lado_rotulo=1)
porta("I_Porta_Fundos", (1.4, 13.0), 0, M["porta_ferro"])

def maco(nome, pai, x, y, z, m, rz=0.0):
    box(nome, (.155, .066, .022), (x, y, z), m, C_INT, pai, rot=(0, 0, rz))
    box(nome + "_Elastico", (.012, .07, .024), (x, y, z), M["elastico"], C_INT, pai, rot=(0, 0, rz))

zt = FZ + .791                                                                                    # tampo da mesa de carteado
r = vazio("I_Dinheiro_Mesa", (CX - .25, CY + .18, zt), C_INT, .4)
for k in range(5): maco("I_Dinheiro_Mesa_Maco", r, (k % 2) * .17, (k // 2) * .075, .012 + (k == 4) * .022, M["nota"] if k % 2 else M["nota2"], rnd.uniform(-.1, .1))
r = vazio("I_Fichas", (CX + .28, CY - .2, zt), C_INT)
for k in range(7):
    m = M[("ficha_r", "ficha_a", "ficha_p", "ficha_b")[k % 4]]; n = rnd.randint(3, 9)
    cyl("I_Fichas_Pilha", .02, .02, .0035 * n, ((k % 4) * .047, (k // 4) * .047, .00175 * n), m, C_INT, r, seg=12)
r = vazio("I_Caderno_Apostas", (RX + .35, RY - .2, FZ + .795), C_INT, .3)
box("I_Caderno_Apostas_Capa", (.16, .22, .018), (0, 0, .009), M["capa"], C_INT, r)
box("I_Caderno_Apostas_Folhas", (.15, .21, .012), (.003, 0, .012), M["papel"], C_INT, r)
ze = FZ + .76                                                                                     # tampo da mesa do escritorio
r = vazio("I_Notebook", (5.42, 11.25, ze), C_INT, -PI / 2)
box("I_Notebook_Base", (.33, .23, .016), (0, 0, .008), M["metal"], C_INT, r)
box("I_Notebook_Tela", (.33, .012, .22), (0, .12, .12), M["metal"], C_INT, r, rot=(-.2, 0, 0))
box("I_Notebook_Tela_Acesa", (.3, .004, .19), (0, .112, .12), M["tela"], C_INT, r, rot=(-.2, 0, 0))
r = vazio("I_Celular", (5.3, 10.95, ze), C_INT, .5)
box("I_Celular_Corpo", (.072, .15, .009), (0, 0, .0045), M["preto_b"], C_INT, r)
r = vazio("I_Caderno_Contabilidade", (5.5, 11.62, ze), C_INT, -.2)
box("I_Caderno_Contabilidade_Capa", (.21, .29, .02), (0, 0, .01), M["preto"], C_INT, r)
box("I_Caderno_Contabilidade_Folhas", (.2, .28, .014), (.003, 0, .013), M["papel"], C_INT, r)
r = vazio("I_Dinheiro_Escondido", (3.95, 12.72, FZ + .5), C_INT)                                  # caixa de sapato na estante do escritorio
box("I_Dinheiro_Escondido_Caixa", (.33, .2, .11), (0, 0, .055), M["papelao"], C_INT, r)
for k in range(4): maco("I_Dinheiro_Escondido_Maco", r, -.08 + (k % 2) * .16, 0, .125 + (k // 2) * .023, M["nota2"] if k % 2 else M["nota"])
r = vazio("I_DVR_Cameras", (3.3, 12.7, FZ + 1.2), C_INT)
box("I_DVR_Cameras_Corpo", (.36, .24, .055), (0, 0, .0275), M["preto"], C_INT, r)
box("I_DVR_Cameras_Luz", (.02, .005, .01), (.13, -.122, .03), M["neon_v"], C_INT, r)
# a estante do escritorio tem prateleiras abertas onde ficam a caixa e o gravador
box("Estante_Escritorio_Vao_A", (.7, .04, .3), (3.95, 12.56, FZ + .65), M["preto"], C_ESC)
box("Estante_Escritorio_Vao_B", (.7, .04, .3), (3.3, 12.56, FZ + 1.3), M["preto"], C_ESC)

# ------------------------------------------------------------------ 8. viatura
r = carro_modelo("Viatura_PM", C_VEIC, "perua", (5.2, -3.3, 0), 0, cor="#eceded", escala=1.08)
if r:
    VTR, sy_, sx_, inf = r
    giroflex(VTR, C_VEIC, -.25, inf["alt"] + .03, larg=1.05)
    faixa_lateral("Viatura_Listra_Azul", VTR, C_VEIC, sy_, -2.0, 1.68, .54, .71, M["faixa_pm"])
    for lado in (1, -1):
        v = "+y" if lado > 0 else "-y"
        texto("Adesivo_Policia_Militar", "POLÍCIA MILITAR", .085, (-.15, sy_(-.15, .89, lado) + lado * .008, .89), v, M["texto_az"], C_VEIC, VTR)
        texto("Adesivo_190", "190", .12, (-1.67, sy_(-1.67, .91, lado) + lado * .008, .91), v, M["texto_az"], C_VEIC, VTR)
        cyl("Brasao_Imagem", .09, .09, .004, (1.03, sy_(1.03, .89, lado) + lado * .006, .89), M["brasao"], C_VEIC, VTR, rot=(PI / 2, 0, 0), seg=28)

# ------------------------------------------------------------------ 9. luzes
def lampada(nome, x, y, watts, cor="#ffd9a0", m="lamp_q", z=FZ + PD - .25, col=C_EST, raio=.12):
    cyl(nome + "_Bulbo", .05, .03, .1, (x, y, z + .06), M[m], col, seg=10)
    luz(nome + "_Luz", "POINT", watts, cor, (x, y, z - .08), C_LUZ, shadow_soft_size=raio)
def tubo(nome, x, y, watts, comp=1.2, ao_longo_x=True, col=C_EST):
    box(nome + "_Tubo", (comp, .05, .04) if ao_longo_x else (.05, comp, .04), (x, y, FZ + PD - .04), M["lamp_f"], col)
    luz(nome + "_Luz", "POINT", watts, "#eaf2ff", (x, y, FZ + PD - .3), C_LUZ, shadow_soft_size=.3)
tubo("Luz_Bar_A", -2.5, 2.2, 55); tubo("Luz_Bar_B", 1.5, 3.6, 55); tubo("Luz_Bar_C", 4.8, 3.0, 40, ao_longo_x=False)
lampada("Luz_Corredor", -4.75, 7.2, 14)
lampada("Luz_Dep_Maquinas", -4.75, 10.8, 12)
lampada("Luz_Dep_Bar", 4.3, 7.5, 16)
lampada("Luz_Salao_Carteado", CX, CY, 26, "#ffcf8a", z=FZ + 2.1, col=C_SAL)
lampada("Luz_Salao_Roleta", RX, RY, 26, "#ffcf8a", z=FZ + 2.1, col=C_SAL)
luz("Luz_Salao_Neon_R", "POINT", 16, "#ff3a3a", (-.5, 6.5, FZ + 2.4), C_LUZ, shadow_soft_size=.4)
luz("Luz_Salao_Neon_V", "POINT", 10, "#3aff8a", (2.0, 7.3, FZ + 2.4), C_LUZ, shadow_soft_size=.4)
tubo("Luz_Escritorio", 4.3, 11.2, 38, ao_longo_x=False, col=C_ESC)
lampada("Luz_Quintal", 0, 13.25, 22, z=FZ + 2.3, col=C_FUN)
lampada("Luz_Beco", -6.2, 6.0, 12, z=FZ + 2.6, col=C_FUN)
luz("Luz_Letreiro", "POINT", 30, "#ffd0a0", (-2, -1.0, 3.3), C_LUZ, shadow_soft_size=.5)

# ------------------------------------------------------------------ 10. pontos do treinamento (lidos pelo site em cena.json)
ponto("Inicio", 3.0, -1.2, (-.6, 1))
ponto("Parceiro", 4.2, -1.0, (-.5, .3))
ponto("Parceiro_Fundos", -7.0, 12.2, (0, 1))
ponto("Parceiro_Salao", -2.6, 6.7, (1, 1))
ponto("Atendente", 4.6, 3.0, (-1, 0))
ponto("Seguranca", -2.9, 7.2, (-1, 0))
ponto("Responsavel", 1.25, 10.9, (-1, 0))
ponto("Apostador_1", -2.1, 11.85, (0, 1))
ponto("Apostador_2", -2.25, 9.9, (-1, 0))
ponto("Apostador_3", 0.4, 6.75, (0, 1))
for i, (x, y) in enumerate(((1.9, 8.6), (1.9, 9.3), (1.3, 12.3), (-.6, 12.0), (-1.4, 6.6), (-2.2, 8.2))):
    ponto("Contencao_%d" % (i + 1), x, y, (-1, 0) if x > 1.5 else (0, -1))
for i, (x, y) in enumerate(((1.85, 12.3), (1.85, 13.7), (-4.8, 15.1), (-7.0, 15.1), (-7.0, 1.0), (-7.0, -1.2), (-16.0, -1.2))):
    ponto("Fuga_%d" % (i + 1), x, y)
ponto("Porta_Salao", -4.75, 5.3, (0, 1)); ponto("Porta_Escritorio", 1.9, 9.85, (1, 0)); ponto("Porta_Fundos", 1.85, 12.4, (0, 1))
ponto("Viatura_Preso", 3.4, -2.2, (1, -.3))

# ------------------------------------------------------------------ 11. cameras, ceu, render
def camera(nome, pos, alvo, lente=22):
    cd = bpy.data.cameras.new(nome); cd.lens = lente; cd.clip_end = 400
    ob = bpy.data.objects.new(nome, cd); C_LUZ.objects.link(ob); ob.location = pos
    ob.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    return ob
camera("Camera_Rua", (1.5, -7.5, 1.75), (-1.5, 1.0, 2.2), 18)
camera("Camera_Bar", (-1.9, 0.9, 1.75), (1.5, 5.5, 1.2), 15)
camera("Camera_Corredor", (-4.75, 5.2, 1.75), (-4.2, 8.5, 1.3), 15)
camera("Camera_Salao", (-3.0, 6.5, 1.75), (0.5, 11.5, 1.1), 14)
camera("Camera_Escritorio", (2.95, 9.4, 1.75), (5.6, 12.6, 1.0), 14)
camera("Camera_Fundos", (5.2, 16.4, 1.75), (-4.0, 13.5, 1.2), 15)
p = camera("Camera_Planta", (0, 6.5, 40.0), (0, 6.5, 0)); p.data.type = "ORTHO"; p.data.ortho_scale = 24; p.data.clip_start = 40 - FZ - PD + .06
p.rotation_euler = (0, 0, 0)
scene.camera = bpy.data.objects["Camera_Rua"]

world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World"); scene.world = world
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (*lin(hx("#1b2640")), 1); bg.inputs["Strength"].default_value = .18
scene.unit_settings.system = "METRIC"
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.engine = "CYCLES"; scene.cycles.samples = 128; scene.cycles.use_denoising = True
for attr, val in (("view_transform", "AgX"), ("look", "AgX - Medium High Contrast")):
    try: setattr(scene.view_settings, attr, val)
    except Exception: pass
scene.view_settings.exposure = 0.0
scene["cs_maquinas"] = len(MAQUINAS)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "cassino.blend"))
tris = 0
dg = bpy.context.evaluated_depsgraph_get()
for o in scene.objects:
    if o.type == "MESH" and not o.hide_render:
        e = o.evaluated_get(dg); m = e.to_mesh(); tris += sum(len(p.vertices) - 2 for p in m.polygons); e.to_mesh_clear()
say("cena criada: %d objetos, ~%d triangulos -> cassino.blend" % (len(bpy.data.objects), tris))
