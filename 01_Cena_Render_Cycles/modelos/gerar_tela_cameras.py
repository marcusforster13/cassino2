"""
Cassino clandestino - gera a imagem do monitor das cameras de seguranca a partir do PROPRIO cenario: quatro quadros
(entrada, bar, salao de jogos e fundos) em preto e branco, com o numero da camera e a hora.

Uso:  blender -b ../cassino.blend --python gerar_tela_cameras.py      (nao salva a cena)
Saida: modelos/monitor_cameras_tela.png  (o cassino.py usa essa imagem na tela do monitor do autor, se existir)

Rode de novo quando o cenario mudar bastante. As pessoas nao aparecem: os personagens so existem no site.
"""
import bpy, os
import numpy as np
from mathutils import Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(AQUI, "_cameras"); os.makedirs(TMP, exist_ok=True)
QW, QH = 512, 312                                 # cada quadro; a tela tem 46 x 28 cm
sc = bpy.context.scene
FZ = .15

# posicao, alvo, exposicao (cameras no alto dos cantos, lente bem aberta)
CAMERAS = [((-4.6, -4.2, FZ + 3.0), (-1.6, .2, FZ + .9), 3.2),        # 01 entrada, da calcada
           ((-5.6, .5, FZ + 2.55), (2.6, 3.4, FZ + .8), 1.6),         # 02 bar
           ((2.25, 6.35, FZ + 2.55), (-1.6, 11.2, FZ + .6), 2.4),     # 03 salao de jogos
           ((-7.3, 15.4, FZ + 2.7), (-1.0, 14.0, FZ + .6), 3.6)]      # 04 fundos
sc.render.engine = "CYCLES"; sc.cycles.samples = 48; sc.cycles.use_denoising = True
try: sc.cycles.device = "GPU"
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = QW, QH, 100
sc.render.image_settings.file_format = "PNG"
quadros = []
for i, (pos, alvo, exp) in enumerate(CAMERAS):
    cam = bpy.data.objects.new("CFTV_%d" % i, bpy.data.cameras.new("CFTV_%d" % i)); sc.collection.objects.link(cam)
    cam.location = pos; cam.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = 15; cam.data.clip_start = .05
    sc.camera = cam; sc.view_settings.exposure = exp
    arq = os.path.join(TMP, "cam_%d.png" % (i + 1)); sc.render.filepath = arq; bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(arq); px = np.empty(QW * QH * 4, np.float32); im.pixels.foreach_get(px); bpy.data.images.remove(im)
    quadros.append(px.reshape(QH, QW, 4)[::-1, :, :3])                 # linha 0 = topo

# letras 5 x 7 para "CAM 01" e a hora
G = {"C": "01110 10001 10000 10000 10000 10001 01110", "A": "01110 10001 10001 11111 10001 10001 10001", "M": "10001 11011 10101 10101 10001 10001 10001",
     "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110", "2": "01110 10001 00001 00010 00100 01000 11111",
     "3": "11110 00001 00001 01110 00001 00001 11110", "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
     "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000", "8": "01110 10001 10001 01110 10001 10001 01110",
     "9": "01110 10001 10001 01111 00001 00010 01100", "-": "00000 00000 00000 11111 00000 00000 00000", ":": "00000 00100 00100 00000 00100 00100 00000", " ": "00000 " * 7}
def escrever(img, texto, x, y, k=2):
    for ch in texto:
        g = np.array([[int(c) for c in lin] for lin in G[ch].split()], np.float32)
        g = np.kron(g, np.ones((k, k), np.float32)); h, w = g.shape
        for dx, dy, v in ((1, 1, 0.0), (0, 0, .95)):                  # sombra e letra
            a = img[y + dy:y + dy + h, x + dx:x + dx + w]; m = g[:a.shape[0], :a.shape[1]] > 0; a[m] = v
        x += w + k

r = np.random.RandomState(7); W, H, B = QW * 2 + 6, QH * 2 + 6, 2
tela = np.full((H, W), .02, np.float32)
for i, q in enumerate(quadros):
    g = q @ np.array([.3, .59, .11], np.float32)
    g = np.clip(g * 1.05 + .03, 0, 1) ** .9                           # contraste de camera barata
    g = np.clip(g + r.normal(0, .025, g.shape), 0, 1)                 # chuvisco
    g[::2] *= .93                                                     # linhas de varredura
    yy, xx = np.mgrid[0:QH, 0:QW]; g *= 1 - .35 * (((xx - QW / 2) / (QW / 2)) ** 2 + ((yy - QH / 2) / (QH / 2)) ** 2) / 2      # cantos escuros
    escrever(g, "CAM 0%d" % (i + 1), 10, 8); escrever(g, "2026-10-13 22:3%d:1%d" % (7, 4 + i), QW - 245, 8)
    x0 = B + (i % 2) * (QW + B); y0 = B + (i // 2) * (QH + B); tela[y0:y0 + QH, x0:x0 + QW] = g
rgb = np.stack([tela * .95, tela, tela * .97, np.ones_like(tela)], 2)[::-1]      # leve tom esverdeado
dst = os.path.join(AQUI, "monitor_cameras_tela.png")
im = bpy.data.images.new("tela_cameras", W, H, alpha=False); im.pixels.foreach_set(rgb.ravel().astype(np.float32)); im.filepath_raw = dst; im.file_format = "PNG"; im.save()
print("[CAMERAS] %s (%d x %d)" % (dst, W, H))
