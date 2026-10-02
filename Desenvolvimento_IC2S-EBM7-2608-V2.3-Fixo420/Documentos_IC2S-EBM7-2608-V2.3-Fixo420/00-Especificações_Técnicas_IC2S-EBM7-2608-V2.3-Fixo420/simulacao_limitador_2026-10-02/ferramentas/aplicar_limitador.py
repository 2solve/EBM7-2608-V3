"""
EBM7 V2.3 Fixo420 -- substitui os TPS26613 (U8-U11) e o TPS7A4001 (U12) por um limitador discreto por laco.
Folha: 06_lacos.kicad_sch (worktree C:\\hw\\wt\\EBM7-420-limitador, rama lacos-limitador-discreto).

Por canal k (U8..U11 -> k=1..4), na linha y0 do canal e com x_O = pino esquerdo do 0R (R10/R11/R12/R16):
  RS  (R40..R43, 18R)  rot 270, ancora (x_O-3.81, y0): pino1 = x_O (sobre o 0R), pino2 = x_S = x_O-7.62
  M1  (Q1..Q4, MOSFET) rot 90,  ancora (x_S-5.08, y0+2.54): D=(x_S-10.16,y0) S=(x_S,y0) G=(x_S-5.08,y0+7.62)
  Q2  (Q5..Q8, NPN)    rot 0,   ancora (x_O-2.54, y0-10.16): B=(x_S,y0-10.16) C=(x_O,y0-15.24) E=(x_O,y0-5.08)
  RG  (R44..R47, 100k) rot 0,   ancora (x_G, y0+11.43): pino1 = G, pino2 = (x_G, y0+15.24)
  fios: juncao do TVS (x_j,y0) -> D ; B -> S ; E -> O ; C -> stub direita + label LIMk_G ; G -> stub direita + label LIMk_G ;
        RG pino2 -> stub direita + label VZ_LIM
Partilhado (zona do antigo U12): +24V_ADC -> R48 22k -> VZ_LIM -> D26 zener 10 V e C50 100n para GND_ADC.
Remove: U8-U12, R22-R26, C26, C29, C31, C32, C37, C38, os simbolos +12V_TPS, as labels VSNS e o que ficar pendurado.
Altera: D6/D7/D8/D11 -> SMBJ36A (DO-214AA); burden R13/R14/R15/R17 -> 1206 (parts.json).
Os dados das pecas vem de parts.json (verificados nas folhas de dados). Le/escreve com LF.
"""
import re, uuid, os, json, shutil, sys

PROJ = r'C:\hw\wt\EBM7-420-limitador\Desenvolvimento_IC2S-EBM7-2608-V2.3-Fixo420\Projeto_IC2S-EBM7-2608-V2.3-Fixo420'
SHEET = os.path.join(PROJ, '06_lacos.kicad_sch')
HERE = os.path.dirname(os.path.abspath(__file__))
KICAD_DEV = r'C:\Program Files\KiCad\10.0\share\kicad\symbols\Device.kicad_sym'
KICAD_FP = r'C:\Program Files\KiCad\10.0\share\kicad\footprints\Package_TO_SOT_SMD.pretty\SOT-223-3_TabPin2.kicad_mod'
PROJECT = 'IC2S-EBM7-2608-V2.3-Fixo420'
SPATH = '/ea39faa7-2c85-4731-99b5-dc619370fd78/729d5fb8-4630-4e1d-b2a5-1a4c2f4e1cd4'
LIB = 'EBM7_V23_proyecto11'
P = json.load(open(os.path.join(HERE, 'parts.json'), encoding='utf8'))

REMOVE_REFS = {'U8', 'U9', 'U10', 'U11', 'U12', 'R22', 'R23', 'R24', 'R25', 'R26',
               'C26', 'C29', 'C31', 'C32', 'C37', 'C38'}
CANAIS = [  # (k, TPS, 0R, TVS, burden)
    (1, 'U8', 'R10', 'D6', 'R13'), (2, 'U9', 'R11', 'D7', 'R14'),
    (3, 'U10', 'R12', 'D8', 'R15'), (4, 'U11', 'R16', 'D11', 'R17')]
EPS = 0.006


def f(v):
    t = ('%.4f' % v).rstrip('0').rstrip('.')
    return '0' if t in ('-0', '') else t


def U():
    return str(uuid.uuid4())


# ------------------------------------------------------------------ s-expr helpers
def sexp_end(s, i):
    """indice logo a seguir ao ')' que fecha o '(' em s[i]."""
    depth = 0; in_str = False; n = len(s)
    while i < n:
        c = s[i]
        if in_str:
            if c == '\\':
                i += 2; continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError('sexp sem fim')


def children(s, start):
    """spans dos filhos directos do s-expr que comeca em s[start]."""
    end = sexp_end(s, start); res = []; i = start + 1; in_str = False
    while i < end - 1:
        c = s[i]
        if in_str:
            if c == '\\':
                i += 2; continue
            if c == '"':
                in_str = False
            i += 1; continue
        if c == '"':
            in_str = True; i += 1; continue
        if c == '(':
            e = sexp_end(s, i); res.append((i, e)); i = e; continue
        i += 1
    return res


def head(t):
    return re.match(r'\((\w+)', t).group(1)


# ------------------------------------------------------------------ parse
s = open(SHEET, encoding='utf8').read()
assert '\r\n' not in s, 'CRLF?'
root = s.index('(kicad_sch')
items = children(s, root)


def parse_items(s):
    root = s.index('(kicad_sch')
    out = []
    for a, b in children(s, root):
        t = s[a:b]; h = head(t); d = dict(a=a, b=b, h=h, t=t)
        if h == 'symbol':
            d['lib_id'] = re.search(r'\(lib_id "([^"]+)"\)', t).group(1)
            m = re.search(r'\n\t\t\(at ([\-\d.]+) ([\-\d.]+) ([\-\d.]+)\)', t)
            d['x'], d['y'], d['rot'] = float(m.group(1)), float(m.group(2)), int(float(m.group(3)))
            mm = re.search(r'\n\t\t\(mirror (\w)\)', t); d['mirror'] = mm.group(1) if mm else None
            d['ref'] = re.search(r'\(property "Reference" "([^"]*)"', t).group(1)
            d['val'] = re.search(r'\(property "Value" "([^"]*)"', t).group(1)
        elif h == 'wire':
            m = re.findall(r'\(xy ([\-\d.]+) ([\-\d.]+)\)', t)
            d['p'] = [(float(m[0][0]), float(m[0][1])), (float(m[1][0]), float(m[1][1]))]
        elif h in ('junction', 'no_connect'):
            m = re.search(r'\(at ([\-\d.]+) ([\-\d.]+)\)', t); d['pt'] = (float(m.group(1)), float(m.group(2)))
        elif h in ('label', 'global_label', 'hierarchical_label'):
            d['name'] = re.match(r'\(\w+ "([^"]*)"', t).group(1)
            m = re.search(r'\(at ([\-\d.]+) ([\-\d.]+)', t); d['pt'] = (float(m.group(1)), float(m.group(2)))
        out.append(d)
    return out


def lib_pins(s):
    """{lib_id: [(num, x, y)]} a partir de lib_symbols (coordenadas da biblioteca, Y para cima)."""
    root = s.index('(kicad_sch')
    for a, b in children(s, root):
        if head(s[a:b]) == 'lib_symbols':
            res = {}
            for c, d in children(s, a):
                t = s[c:d]; name = re.match(r'\(symbol "([^"]+)"', t).group(1); pins = []
                for m in re.finditer(r'\(pin \w+ \w+', t):
                    e = sexp_end(t, m.start()); pt = t[m.start():e]
                    at = re.search(r'\(at ([\-\d.]+) ([\-\d.]+)', pt); num = re.search(r'\(number "([^"]*)"', pt).group(1)
                    pins.append((num, float(at.group(1)), float(at.group(2))))
                res[name] = pins
            return res, (a, b)
    raise ValueError('sem lib_symbols')


def xf(x, y, rot, mirror=None):
    """biblioteca (Y para cima) -> esquema (Y para baixo), rotacao anti-horaria visual."""
    x, y = x, -y
    if rot == 90:
        x, y = y, -x
    elif rot == 180:
        x, y = -x, -y
    elif rot == 270:
        x, y = -y, x
    if mirror == 'x':
        y = -y
    elif mirror == 'y':
        x = -x
    return x, y


def pin_points(sym, pins):
    pts = []
    for num, px, py in pins.get(sym['lib_id'], []):
        dx, dy = xf(px, py, sym['rot'], sym['mirror'])
        pts.append((num, (round(sym['x'] + dx, 4), round(sym['y'] + dy, 4))))
    return pts


def same(p, q):
    return abs(p[0] - q[0]) < EPS and abs(p[1] - q[1]) < EPS


def on_seg(p, a, b):
    if same(p, a) or same(p, b):
        return False
    if abs(a[0] - b[0]) < EPS and abs(p[0] - a[0]) < EPS:
        return min(a[1], b[1]) - EPS < p[1] < max(a[1], b[1]) + EPS
    if abs(a[1] - b[1]) < EPS and abs(p[1] - a[1]) < EPS:
        return min(a[0], b[0]) - EPS < p[0] < max(a[0], b[0]) + EPS
    return False


# ------------------------------------------------------------------ 1) remocao + limpeza do que fica pendurado
its = parse_items(s)
pins, _ = lib_pins(s)
assert not [d for d in its if d['h'] == 'symbol' and d['mirror']], 'ha simbolos espelhados: rever xf()'
geo = {}   # ref -> {num: pt}
for d in its:
    if d['h'] == 'symbol':
        geo[d['ref']] = dict(pin_points(d, pins))
# geometria dos canais ANTES de remover (TPS, 0R, TVS)
canal_geo = {}
for k, tps, r0, tvs, rb in CANAIS:
    sym0 = [d for d in its if d['h'] == 'symbol' and d['ref'] == r0][0]
    left = min(geo[r0].values(), key=lambda p: p[0])
    tvsk = geo[tvs]['1']                       # catodo do TVS (pino 1 = K)
    y0 = left[1]
    # juncao do TVS na linha: ponto (x_TVS, y0)
    canal_geo[k] = dict(xO=left[0], y0=y0, xj=tvsk[0])

removed = set()
for d in its:
    if d['h'] == 'symbol' and (d['ref'] in REMOVE_REFS or (d['lib_id'].startswith('power:') and d['val'] == '+12V_TPS')):
        removed.add(d['a'])
    if d['h'] == 'label' and d['name'] == 'VSNS':
        removed.add(d['a'])


def connectivity(its, removed):
    pts_pin = []; pts_lab = []
    for d in its:
        if d['a'] in removed:
            continue
        if d['h'] == 'symbol':
            pts_pin += [p for _, p in pin_points(d, pins)]
        elif d['h'] in ('label', 'global_label', 'hierarchical_label'):
            pts_lab.append(d['pt'])
    wires = [d for d in its if d['h'] == 'wire' and d['a'] not in removed]
    return pts_pin, pts_lab, wires


def dangling_ends(its, removed):
    pts_pin, pts_lab, wires = connectivity(its, removed)
    bad = []
    for w in wires:
        for e in w['p']:
            ok = any(same(e, p) for p in pts_pin) or any(same(e, p) for p in pts_lab)
            ok = ok or any((same(e, o['p'][0]) or same(e, o['p'][1]) or on_seg(e, *o['p'])) for o in wires if o is not w)
            if not ok:
                bad.append((w['a'], e))
    return bad


base_bad = {(a, e) for a, e in dangling_ends(its, set())}
print('extremos pendurados antes:', len(base_bad))
while True:
    novos = [(a, e) for a, e in dangling_ends(its, removed) if (a, e) not in base_bad]
    if not novos:
        break
    for a, e in novos:
        removed.add(a)
# simbolos de alimentacao que ficaram isolados
pts_pin, pts_lab, wires = connectivity(its, removed)
for d in its:
    if d['a'] in removed or d['h'] != 'symbol' or not d['lib_id'].startswith('power:'):
        continue
    pp = [p for _, p in pin_points(d, pins)]
    other_pins = [p for o in its if o['h'] == 'symbol' and o['a'] not in removed and o is not d for _, p in pin_points(o, pins)]
    ok = any(same(p, q) for p in pp for w in wires for q in w['p']) or any(same(p, q) for p in pp for q in other_pins) \
        or any(on_seg(p, *w['p']) for p in pp for w in wires)
    if not ok:
        removed.add(d['a'])
# no_connect sem pino
pts_pin, pts_lab, wires = connectivity(its, removed)
for d in its:
    if d['h'] == 'no_connect' and d['a'] not in removed and not any(same(d['pt'], p) for p in pts_pin):
        removed.add(d['a'])


def junction_ok(pt, its, removed, extra_wires=(), extra_pins=()):
    pts_pin, pts_lab, wires = connectivity(its, removed)
    n = sum(1 for p in list(pts_pin) + list(extra_pins) if same(pt, p))
    for w in list(wires) + [dict(p=p) for p in extra_wires]:
        if same(pt, w['p'][0]) or same(pt, w['p'][1]):
            n += 1
        elif on_seg(pt, *w['p']):
            n += 2
    n += sum(1 for p in pts_lab if same(pt, p))
    return n


rem_report = {}
for d in its:
    if d['a'] in removed:
        key = d['h'] + (':' + d.get('ref', d.get('name', '')) if d['h'] in ('symbol', 'label') else '')
        rem_report[key] = rem_report.get(key, 0) + 1

# ------------------------------------------------------------------ 2) novos elementos
new_items = []      # textos s-expr a inserir
new_wires = []      # [(p1,p2)]
new_pins = []       # pontos de pino novos (para juncoes)
new_labels = []


def prop(name, val, x, y, ang, hide=False, justify='left'):
    j = f'\n\t\t\t\t(justify {justify})' if justify else ''
    h = '\n\t\t\t(hide yes)' if hide else ''
    return (f'\n\t\t(property "{name}" "{val}"\n\t\t\t(at {f(x)} {f(y)} {ang}){h}\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)'
            f'\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t){j}\n\t\t\t)\n\t\t)')


def symbol(lib_id, ref, val, x, y, rot, fp, ds, desc, mpn, pinnums, refxy, valxy, tol=None):
    t = (f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at {f(x)} {f(y)} {rot})\n\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)'
         f'\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)\n\t\t(uuid "{U()}")')
    t += prop('Reference', ref, refxy[0], refxy[1], rot)
    t += prop('Value', val, valxy[0], valxy[1], rot)
    t += prop('Footprint', fp, x, y, rot, hide=True, justify=None)
    t += prop('Datasheet', ds, x, y, 0, hide=True, justify=None)
    t += prop('Description', desc, x, y, 0, hide=True, justify=None)
    t += prop('MPN', mpn, x, y, 0, hide=True, justify=None)
    if tol:
        t += prop('Tolerance', tol, x, y, 0, hide=True, justify=None)
    for n in pinnums:
        t += f'\n\t\t(pin "{n}"\n\t\t\t(uuid "{U()}")\n\t\t)'
    t += (f'\n\t\t(instances\n\t\t\t(project "{PROJECT}"\n\t\t\t\t(path "{SPATH}"\n\t\t\t\t\t(reference "{ref}")'
          f'\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)')
    new_items.append(t)


def wire(p1, p2):
    new_wires.append((p1, p2))
    new_items.append(f'\t(wire\n\t\t(pts\n\t\t\t(xy {f(p1[0])} {f(p1[1])}) (xy {f(p2[0])} {f(p2[1])})\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)'
                     f'\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "{U()}")\n\t)')


def label(name, p, ang=0):
    new_labels.append(p)
    j = 'left bottom' if ang == 0 else 'right bottom'
    new_items.append(f'\t(label "{name}"\n\t\t(at {f(p[0])} {f(p[1])} {ang})\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)'
                     f'\n\t\t\t(justify {j})\n\t\t)\n\t\t(uuid "{U()}")\n\t)')


def text(txt, p):
    new_items.append(f'\t(text "{txt}"\n\t\t(exclude_from_sim no)\n\t\t(at {f(p[0])} {f(p[1])} 0)\n\t\t(effects\n\t\t\t(font'
                     f'\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{U()}")\n\t)')


pwr_n = [155]


def power_from(template_ref, p):
    tpl = [d for d in its if d['h'] == 'symbol' and d['ref'] == template_ref][0]['t']
    ref = f'#PWR{pwr_n[0]:04d}'; pwr_n[0] += 1
    m = re.search(r'\n\t\t\(at ([\-\d.]+) ([\-\d.]+) ([\-\d.]+)\)', tpl)
    ox, oy = float(m.group(1)), float(m.group(2)); dx, dy = p[0] - ox, p[1] - oy
    t = re.sub(r'\(at ([\-\d.]+) ([\-\d.]+)( [\-\d.]+)?\)',
               lambda mm: f'(at {f(float(mm.group(1)) + dx)} {f(float(mm.group(2)) + dy)}{mm.group(3) or ""})', tpl)
    t = re.sub(r'\(uuid "[^"]+"\)', lambda mm: f'(uuid "{U()}")', t)
    t = t.replace(f'"{template_ref}"', f'"{ref}"')
    new_items.append('\t' + t.lstrip('\t'))
    new_pins.append(p)
    return ref


PM, PN, PZ, PB = P['MOS'], P['NPN'], P['DZ'], P['BURDEN']
MOS_ID, NPN_ID = f'{LIB}:{PM["symbol"]}', f'{LIB}:{PN["symbol"]}'
for k, tps, r0, tvs, rb in CANAIS:
    g = canal_geo[k]; xO, y0, xj = g['xO'], g['y0'], g['xj']
    xS = xO - 7.62; xD = xS - 10.16; xG = xS - 5.08
    rs, rg, qm, qn = f'R{39 + k}', f'R{43 + k}', f'Q{k}', f'Q{4 + k}'
    symbol('Device:R', rs, '18R', xO - 3.81, y0, 270, 'EBM7_V23:0603R', '', P['RS']['desc'], P['RS']['mpn'], ['1', '2'],
           (xO - 0.635, y0 - 1.905), (xO - 0.635, y0 + 3.175), tol='1%')
    symbol(MOS_ID, qm, PM['value'], xS - 5.08, y0 + 2.54, 90, PM['fp'], PM['ds'], PM['desc'], PM['mpn'], ['1', '2', '3'],
           (xD + 0.635, y0 - 3.81), (xD + 0.635, y0 - 1.27))
    symbol(NPN_ID, qn, PN['value'], xO - 2.54, y0 - 10.16, 0, PN['fp'], PN['ds'], PN['desc'], PN['mpn'], ['1', '2', '3'],
           (xO + 1.27, y0 - 11.43), (xO + 1.27, y0 - 8.89))
    symbol('Device:R', rg, '100k', xG, y0 + 11.43, 0, 'EBM7_V23:0603R', '', P['RG']['desc'], P['RG']['mpn'], ['1', '2'],
           (xG + 1.905, y0 + 11.43), (xG + 1.905, y0 + 13.97), tol='1%')
    new_pins += [(xO, y0), (xS, y0), (xS, y0), (xD, y0), (xG, y0 + 7.62), (xS, y0 - 10.16), (xO, y0 - 15.24),
                 (xO, y0 - 5.08), (xG, y0 + 7.62), (xG, y0 + 15.24)]   # RS1, RS2+S, D, G+RG1, B, C, E, RG2
    wire((xj, y0), (xD, y0))                         # juncao do TVS -> dreno
    wire((xS, y0 - 10.16), (xS, y0))                 # base -> fonte/RS
    wire((xO, y0 - 5.08), (xO, y0))                  # emissor -> no do 0R
    wire((xO, y0 - 15.24), (xO + 5.08, y0 - 15.24))  # colector -> label
    label(f'LIM{k}_G', (xO + 5.08, y0 - 15.24))
    wire((xG, y0 + 7.62), (xG + 5.08, y0 + 7.62))    # porta -> label
    label(f'LIM{k}_G', (xG + 5.08, y0 + 7.62))
    wire((xG, y0 + 15.24), (xG, y0 + 17.78))         # RG -> VZ_LIM (abaixo do texto do RG)
    label('VZ_LIM', (xG, y0 + 17.78))

# partilhado: zona do antigo U12
X0, Y0 = 226.06, 25.4
power_from('#PWR0119', (X0, Y0))                                  # +24V_ADC
symbol('Device:R', 'R48', '22k', X0, Y0 + 5.08, 0, 'EBM7_V23:0603R', '', P['RZ']['desc'], P['RZ']['mpn'], ['1', '2'],
       (X0 + 1.905, Y0 + 3.81), (X0 + 1.905, Y0 + 6.35), tol='1%')
new_pins += [(X0, Y0 + 1.27), (X0, Y0 + 8.89)]
wire((X0, Y0), (X0, Y0 + 1.27))
wire((X0, Y0 + 8.89), (X0, Y0 + 12.7))
symbol('Device:D_Zener', 'D26', PZ['value'], X0, Y0 + 16.51, 270, PZ['fp'], PZ['ds'], PZ['desc'], PZ['mpn'], ['1', '2'],
       (X0 - 1.905, Y0 + 15.24), (X0 - 1.905, Y0 + 17.78))
new_pins += [(X0, Y0 + 12.7), (X0, Y0 + 20.32)]
power_from('#PWR099', (X0, Y0 + 20.32))                          # GND_ADC
wire((X0, Y0 + 12.7), (X0 + 12.7, Y0 + 12.7))
symbol('Device:C', 'C50', '100nF/50V', X0 + 12.7, Y0 + 16.51, 0, 'EBM7_V23:0603C', '', P['CZ']['desc'], P['CZ']['mpn'], ['1', '2'],
       (X0 + 14.605, Y0 + 15.24), (X0 + 14.605, Y0 + 17.78))
new_pins += [(X0 + 12.7, Y0 + 12.7), (X0 + 12.7, Y0 + 20.32)]
power_from('#PWR099', (X0 + 12.7, Y0 + 20.32))
wire((X0 + 12.7, Y0 + 12.7), (X0 + 20.32, Y0 + 12.7))
label('VZ_LIM', (X0 + 20.32, Y0 + 12.7))

# nota de decisao (zona do antigo divisor VSNS)
NOTA = P['nota']
for i, linha in enumerate(NOTA):
    text(linha, (208.28, 55.88 + 2.54 * i))

# ------------------------------------------------------------------ 3) montar o ficheiro
keep = [d for d in its if d['a'] not in removed]
# alteracoes de propriedades (TVS e burden)
def set_prop(t, name, val):
    t2, n = re.subn(r'(\(property "' + re.escape(name) + r'" ")([^"]*)(")', lambda m: m.group(1) + val + m.group(3), t, count=1)
    assert n == 1, (name, t[:80])
    return t2


edits = {}
for k, tps, r0, tvs, rb in CANAIS:
    edits[tvs] = [('Value', P['TVS']['value']), ('Footprint', P['TVS']['fp']), ('MPN', P['TVS']['mpn'])]
    edits[rb] = [('Footprint', PB['fp']), ('MPN', PB['mpn'])]
out = s[:items[0][0]]
prev_end = items[0][0]
# reconstruir preservando a ordem e o whitespace entre itens
pieces = []
last = root + len('(kicad_sch')
for d in its:
    gap = s[last:d['a']]
    if d['a'] in removed:
        last = d['b']; continue
    t = d['t']
    if d['h'] == 'symbol' and d['ref'] in edits:
        for name, val in edits[d['ref']]:
            t = set_prop(t, name, val)
    pieces.append(gap + t); last = d['b']
tail = s[last:]
body = ''.join(pieces)
# juncoes necessarias nos pontos novos (>= 3 ligacoes) e que ainda nao existam
its_keep = [d for d in its if d['a'] not in removed]
ex_junc = [d['pt'] for d in its_keep if d['h'] == 'junction']
cands = set()
for p in new_pins + [w[0] for w in new_wires] + [w[1] for w in new_wires]:
    cands.add((round(p[0], 4), round(p[1], 4)))
add_j = []
for pt in sorted(cands):
    n = junction_ok(pt, its, removed, extra_wires=new_wires, extra_pins=new_pins)
    if n >= 3 and not any(same(pt, q) for q in ex_junc):
        add_j.append(pt)
for pt in add_j:
    new_items.append(f'\t(junction\n\t\t(at {f(pt[0])} {f(pt[1])})\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "{U()}")\n\t)')
# juncoes que ficaram com menos de 3 ligacoes (por causa da remocao) saem
body2 = []
for piece in pieces:
    m = re.search(r'\(junction\s*\(at ([\-\d.]+) ([\-\d.]+)\)', piece)
    if m and piece.lstrip().startswith('(junction'):
        pt = (float(m.group(1)), float(m.group(2)))
        if junction_ok(pt, its, removed, extra_wires=new_wires, extra_pins=new_pins) < 3:
            rem_report['junction(<3)'] = rem_report.get('junction(<3)', 0) + 1
            continue
    body2.append(piece)
new_txt = ''.join('\n' + t for t in new_items)
ef = [i for i, pc in enumerate(body2) if pc.lstrip().startswith('(embedded_fonts')]
if ef:
    body2.insert(ef[0], new_txt)
    body = ''.join(body2)
else:
    body = ''.join(body2) + new_txt
s_new = s[:root + len('(kicad_sch')] + body + tail

# lib_symbols: tirar os que deixaram de ser usados e juntar os novos
def lib_block(src, name, newname, pinmap, props):
    i = src.index(f'(symbol "{name}"\n'); e = sexp_end(src, i); t = src[i:e]
    assert '(extends' not in t[:200], 'simbolo com extends'
    t = t.replace(f'(symbol "{name}"', f'(symbol "{newname}"', 1)
    t = re.sub(r'\(symbol "' + re.escape(name) + r'_(\d+)_(\d+)"', lambda m: f'(symbol "{props["Value"]}_{m.group(1)}_{m.group(2)}"', t)
    for old, new in pinmap.items():
        t, n = re.subn(r'(\(number ")' + re.escape(old) + r'(")', lambda m: m.group(1) + new + m.group(2), t)
        assert n == 1, (name, old, n)
    for pn, pv in props.items():
        t, n = re.subn(r'(\(property "' + re.escape(pn) + r'" ")([^"]*)(")', lambda m: m.group(1) + pv + m.group(3), t, count=1)
        assert n == 1, (pn,)
    # tirar propriedades de simulacao (mapeavam os nomes de pinos antigos)
    while True:
        m = re.search(r'\n\t*\(property "Sim\.[^"]*"', t)
        if not m:
            break
        a = m.start() + 1 + len(re.match(r'\n(\t*)', t[m.start():]).group(1)); e2 = sexp_end(t, a)
        t = t[:m.start()] + t[e2:]
    return t


dev = open(KICAD_DEV, encoding='utf8').read()
dev = dev.replace('\r\n', '\n')
mos_t = lib_block(dev, 'Q_NMOS', PM['symbol'], PM['pinmap'],
                  {'Value': PM['symbol'], 'Footprint': PM['fp'], 'Datasheet': PM['ds'], 'Description': PM['desc']})
npn_t = lib_block(dev, 'Q_NPN', PN['symbol'], PN['pinmap'],
                  {'Value': PN['symbol'], 'Footprint': PN['fp'], 'Datasheet': PN['ds'], 'Description': PN['desc']})
# biblioteca do projecto
libfile = os.path.join(PROJ, 'symbols', LIB + '.kicad_sym')
open(libfile, 'w', encoding='utf8', newline='\n').write(
    '(kicad_symbol_lib\n\t(version 20251024)\n\t(generator "aplicar_limitador")\n\t(generator_version "10.0")\n\t'
    + mos_t + '\n\t' + npn_t + '\n)\n')


def indent1(t):
    return '\n'.join(('\t' + l) if l.strip() else l for l in t.split('\n'))


emb_mos = indent1(mos_t).replace(f'(symbol "{PM["symbol"]}"', f'(symbol "{MOS_ID}"', 1)
emb_npn = indent1(npn_t).replace(f'(symbol "{PN["symbol"]}"', f'(symbol "{NPN_ID}"', 1)
_, (la, lb) = lib_pins(s_new)
lib_t = s_new[la:lb]
for dead in ('EBM7_V23_proyecto7:TPS26613DDFR', 'EBM7_V23_proyecto9:TPS7A4001DGN'):
    if f'"{dead}"' not in s_new[lb:]:
        i = lib_t.index(f'(symbol "{dead}"'); e = sexp_end(lib_t, i)
        j = lib_t.rfind('\n', 0, i)
        lib_t = lib_t[:j] + lib_t[e:]
        rem_report['lib_symbols:' + dead] = 1
if '"power:+5V"' not in s_new[lb:]:
    i = lib_t.index('(symbol "power:+5V"'); e = sexp_end(lib_t, i); j = lib_t.rfind('\n', 0, i)
    lib_t = lib_t[:j] + lib_t[e:]; rem_report['lib_symbols:power:+5V'] = 1
close = lib_t.rindex('\n\t)')
lib_t = lib_t[:close] + '\n\t\t' + emb_mos.lstrip('\t') + '\n\t\t' + emb_npn.lstrip('\t') + lib_t[close:]
s_new = s_new[:la] + lib_t + s_new[lb:]
open(SHEET, 'w', encoding='utf8', newline='\n').write(s_new)

# footprint SOT-223 com a aba no pino 2
fpdst = os.path.join(PROJ, 'footprints', 'EBM7_V23.pretty', 'SOT-223-3_TabPin2.kicad_mod')
fpt = open(KICAD_FP, encoding='utf8').read().replace('\r\n', '\n')
fpt = re.sub(r'\(descr "([^"]*)"', lambda m: '(descr "Copia da biblioteca KiCad 10 Package_TO_SOT_SMD:SOT-223-3_TabPin2 (aba = pad 2 = dreno), 2026-10-02. '
             + m.group(1).replace('"', "'") + '"', fpt, count=1)
open(fpdst, 'w', encoding='utf8', newline='\n').write(fpt)
# sym-lib-table
slt = os.path.join(PROJ, 'sym-lib-table'); t = open(slt, encoding='utf8').read()
if LIB not in t:
    t = t.rstrip().rstrip(')') + (f'\t(lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/symbols/{LIB}.kicad_sym")(options "")'
                                  f'(descr "{P["lib_descr"]}"))\n)\n')
    open(slt, 'w', encoding='utf8', newline='\n').write(t)

json.dump(dict(removidos=rem_report, juncoes_novas=add_j, canais=canal_geo), open(os.path.join(HERE, 'aplicar_relatorio.json'), 'w'), indent=1)
print('removidos:', json.dumps(rem_report, indent=0))
print('juncoes novas:', len(add_j), '| itens novos:', len(new_items))
