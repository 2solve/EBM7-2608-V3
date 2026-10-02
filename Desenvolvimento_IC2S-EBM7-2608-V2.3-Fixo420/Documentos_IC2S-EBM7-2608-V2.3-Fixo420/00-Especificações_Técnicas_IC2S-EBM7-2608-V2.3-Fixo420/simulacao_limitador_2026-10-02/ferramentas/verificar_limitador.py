"""
Portas de verificacao da alteracao 'limitador discreto' (EBM7 V2.3 Fixo420, worktree lacos-limitador-discreto).
1) netlist: remocoes/adicoes exactas; a particao dos pinos NAO tocados e identica a de antes; redes novas com os
   membros exactos esperados; +12V_TPS e VSNS desaparecem; propriedades alteradas so onde previsto.
2) ERC: 0 erros; avisos comparados com a linha de base.
3) PDF da folha 7 renderizado para inspeccao visual.
Sai com codigo 1 se alguma porta falhar.
"""
import json, os, subprocess, sys, re
from collections import Counter, defaultdict
sys.path.insert(0, r'C:\Users\Javier Rivadineira\.claude\jobs\ef5da2a8\tmp')
import parse as px

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = r'C:\hw\wt\EBM7-420-limitador\Desenvolvimento_IC2S-EBM7-2608-V2.3-Fixo420\Projeto_IC2S-EBM7-2608-V2.3-Fixo420'
SCH = os.path.join(PROJ, 'IC2S-EBM7-2608-V2.3-Fixo420.kicad_sch')
K = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
P = json.load(open(os.path.join(HERE, 'parts.json'), encoding='utf8'))
falhas = []


def chk(cond, msg):
    print(('  OK   ' if cond else '  FALHA ') + msg)
    if not cond:
        falhas.append(msg)


subprocess.run([K, 'sch', 'export', 'netlist', '--format', 'kicadsexpr', '-o', os.path.join(HERE, 'depois.net'), SCH],
               capture_output=True, text=True)
ca, na = px.load(os.path.join(HERE, 'antes.net'))
cd, nd = px.load(os.path.join(HERE, 'depois.net'))

REM = {'U8', 'U9', 'U10', 'U11', 'U12', 'R22', 'R23', 'R24', 'R25', 'R26', 'C26', 'C29', 'C31', 'C32', 'C37', 'C38'}
NEW = {f'Q{i}' for i in range(1, 9)} | {f'R{i}' for i in range(40, 49)} | {'D26', 'C50'}
print('1) componentes')
chk(set(ca) - set(cd) == REM, f'removidos = {sorted(set(ca) - set(cd))}')
chk(set(cd) - set(ca) == NEW, f'adicionados = {sorted(set(cd) - set(ca))}')
mud = {r for r in set(ca) & set(cd) if ca[r][:2] != cd[r][:2]}
esperado_mud = {'D6', 'D7', 'D8', 'D11', 'R13', 'R14', 'R15', 'R17'}
chk(mud == esperado_mud, f'valor/footprint alterados = {sorted(mud)}')
for r in ('D6', 'D7', 'D8', 'D11'):
    chk(cd[r][0] == P['TVS']['value'] and cd[r][1] == P['TVS']['fp'], f'{r}: {cd[r][0]} {cd[r][1]}')
for r in ('R13', 'R14', 'R15', 'R17'):
    chk(cd[r][0] == '110R' and cd[r][1] == P['BURDEN']['fp'], f'{r}: {cd[r][0]} {cd[r][1]}')
for r in [f'Q{i}' for i in range(1, 5)]:
    chk(cd[r][1] == P['MOS']['fp'], f'{r} footprint {cd[r][1]}')
for r in [f'Q{i}' for i in range(5, 9)]:
    chk(cd[r][1] == P['NPN']['fp'], f'{r} footprint {cd[r][1]}')


def pin2net(nets):
    m = {}
    for n, nodes in nets.items():
        for r, p, _ in nodes:
            m[(r, p)] = n
    return m


ma, md = pin2net(na), pin2net(nd)
print('2) particao dos pinos nao tocados')
keep = [k for k in ma if k[0] not in REM and k[0] not in NEW]
grp_a, grp_d = defaultdict(set), defaultdict(set)
for k in keep:
    grp_a[ma[k]].add(k)
    if k in md:
        grp_d[md[k]].add(k)
chk(all(k in md for k in keep), 'todos os pinos nao tocados continuam no netlist')
pa = sorted(sorted(v) for v in grp_a.values())
pd = sorted(sorted(v) for v in grp_d.values())
chk(pa == pd, f'particao identica ({len(pa)} grupos antes, {len(pd)} depois)')
if pa != pd:
    sa, sd = {tuple(x) for x in pa}, {tuple(x) for x in pd}
    print('     so antes:', [x for x in sa - sd][:6]); print('     so depois:', [x for x in sd - sa][:6])

print('3) redes novas (membros exactos)')
def members(pin):
    n = md.get(pin)
    return n, {(r, p) for r, p, _ in nd.get(n, [])}


R0 = {1: 'R10', 2: 'R11', 3: 'R12', 4: 'R16'}
TVS = {1: 'D6', 2: 'D7', 3: 'D8', 4: 'D11'}
P2AIN = {1: '7', 2: '9', 3: '11', 4: '13'}
pm, pn = P['MOS']['pinmap'], P['NPN']['pinmap']   # nome -> numero
for k in range(1, 5):
    qm, qn, rs, rg = f'Q{k}', f'Q{4 + k}', f'R{39 + k}', f'R{43 + k}'
    D, G, S = (qm, pm['D']), (qm, pm['G']), (qm, pm['S'])
    B, C, E = (qn, pn['B']), (qn, pn['C']), (qn, pn['E'])
    n, m = members(D); chk(('P2', P2AIN[k]) in m and (TVS[k], '1') in m, f'canal {k}: dreno {qm} na rede {n} com P2.{P2AIN[k]} e {TVS[k]}.K')
    n, m = members(S); chk(m == {S, (rs, '2'), B}, f'canal {k}: fonte {n} = {sorted(m)}')
    n, m = members(E); chk(m == {E, (rs, '1'), (R0[k], '2')}, f'canal {k}: emissor/OUT {n} = {sorted(m)}')
    n, m = members(G); chk(m == {G, C, (rg, '1')}, f'canal {k}: porta {n} = {sorted(m)}')
n, m = members(('R48', '2'))
chk(m == {('R44', '2'), ('R45', '2'), ('R46', '2'), ('R47', '2'), ('R48', '2'), ('D26', '1'), ('C50', '1')}, f'VZ {n} = {sorted(m)}')
chk(md.get(('R48', '1')) == '+24V_ADC', f'R48.1 em {md.get(("R48", "1"))}')
chk(md.get(('D26', '2')) == 'GND_ADC' and md.get(('C50', '2')) == 'GND_ADC', 'D26.A e C50.2 em GND_ADC')
chk('+12V_TPS' not in nd and not any(x.endswith('VSNS') for x in nd), 'redes +12V_TPS e VSNS desapareceram')

print('4) ERC')
erc = os.path.join(HERE, 'erc_depois.json')
subprocess.run([K, 'sch', 'erc', '--format', 'json', '--severity-all', '-o', erc, SCH], capture_output=True, text=True)
v = [x for s_ in json.load(open(erc))['sheets'] for x in s_['violations']]
cnt = Counter((x['severity'], x['type']) for x in v)
base = Counter({('warning', 'lib_symbol_issues'): 288, ('warning', 'isolated_pin_label'): 9, ('warning', 'same_local_global_label'): 1})
print('   antes :', dict(base)); print('   depois:', dict(cnt))
chk(sum(c for (sev, _), c in cnt.items() if sev == 'error') == 0, 'ERC sem erros')
novos = {k: c for k, c in cnt.items() if c > base.get(k, 0)}
for (sev, typ), c in novos.items():
    det = [x for x in v if x['type'] == typ][:4]
    print(f'   novo/aumentou: {sev} {typ} {c}:', [d['description'][:70] + ' ' + str([i['description'][:40] for i in d['items']]) for d in det])
chk(not [k for k in novos if k[1] != 'lib_symbol_issues'], 'sem avisos novos alem de lib_symbol_issues')

print('5) render')
pdf = os.path.join(HERE, 'depois.pdf')
subprocess.run([K, 'sch', 'export', 'pdf', '-o', pdf, SCH], capture_output=True, text=True)
import fitz
d = fitz.open(pdf)
for i, pg in enumerate(d):
    if 'Lacos 4-20mA' in pg.get_text() or 'VZ_LIM' in pg.get_text():
        pg.get_pixmap(dpi=110).save(os.path.join(HERE, f'depois_p{i + 1}.png'))
        clip = fitz.Rect(0, 0, pg.rect.width * 0.36, pg.rect.height)
        pg.get_pixmap(dpi=220, clip=clip).save(os.path.join(HERE, f'depois_p{i + 1}_esq.png'))
        print('   pagina', i + 1, 'renderizada')
print('\nRESULTADO:', 'PASSA' if not falhas else f'FALHA ({len(falhas)})')
sys.exit(1 if falhas else 0)
