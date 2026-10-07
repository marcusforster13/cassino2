"""Carimba a versao do site (data e hora) em 04_ThreeJS/web/index.html. Rodar antes de cada envio ao GitHub:
o numero entra no endereco de todos os arquivos, e o navegador (inclusive o do Quest) baixa tudo de novo."""
import io, os, re, time
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "04_ThreeJS", "web", "index.html")
s = io.open(p, encoding="utf-8").read(); v = time.strftime("%m%d-%H%M")
s, n = re.subn(r"const VERSAO = '[^']*';", "const VERSAO = '%s';" % v, s); assert n == 1
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
io.open(os.path.join(os.path.dirname(p), "versao.json"), "w", encoding="utf-8").write('{"versao": "%s"}' % v)      # a pagina compara com este arquivo ao abrir
print("[VERSAO] " + v)
