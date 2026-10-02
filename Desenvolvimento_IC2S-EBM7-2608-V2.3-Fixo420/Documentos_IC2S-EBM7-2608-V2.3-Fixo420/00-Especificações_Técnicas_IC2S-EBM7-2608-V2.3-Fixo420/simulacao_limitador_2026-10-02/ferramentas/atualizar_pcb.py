"""Actualiza a PCB a partir do netlist do esquemático — o equivalente ao «Update PCB from Schematic» (F8) do KiCad,
em modo de linha de comandos, com estas opções:

  - ligação por path (UUID); se o path não existir, re-liga pela referência e actualiza o path, o sheetname e o
    sheetfile (opção «Re-link footprints ... reference designators»). Não apaga nem duplica footprints que só
    mudaram de folha;
  - apaga os footprints sem símbolo;
  - substitui os footprints cujo símbolo pede outro. Mantém a posição, a face e os textos. A orientação escolhida é,
    entre θ e θ+180°, a que deixa cada número de pad onde estava. O KiCad mantém θ, e se o pad 1 mudar de lado no
    footprint novo, a pista antiga fica no pad errado;
  - actualiza o valor e os campos de utilizador; o Datasheet e a Description só nos footprints novos ou substituídos;
  - aplica as redes do netlist aos pads. As pistas, vias e zonas de uma rede cujos pads passaram todos para outra
    seguem-nos, como no F8. As pistas que ficam sem pads não se apagam: são reportadas;
  - os footprints novos ficam estacionados abaixo da placa, agrupados pelas redes que partilham. Não são
    posicionados (o F8 também os deixa fora da placa).

Uso (com o Python do KiCad 10, o único que importa o pcbnew):
  "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" atualizar_pcb.py PLACA.kicad_pcb NETLIST.net SAIDA.kicad_pcb [--dry-run]
O netlist sai de: kicad-cli sch export netlist --format kicadsexpr -o NETLIST.net RAIZ.kicad_sch
"""
import os
import re
import sys
import collections

import pcbnew

TOK = re.compile(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+')


def sexp(s):
    st = [[]]
    for t in TOK.findall(s):
        if t == '(':
            st.append([])
        elif t == ')':
            x = st.pop()
            st[-1].append(x)
        else:
            st[-1].append(t[1:-1].replace('\\"', '"').replace('\\\\', '\\') if t.startswith('"') else t)
    return st[0][0]


def get(l, k):
    for x in l:
        if isinstance(x, list) and x and x[0] == k:
            return x
    return None


def natkey(s):
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)]


def ler_netlist(fn):
    d = sexp(open(fn, encoding='utf8').read())
    comps = collections.OrderedDict()
    for c in get(d, 'components')[1:]:
        ref = get(c, 'ref')[1]
        sp = get(c, 'sheetpath')
        props = {}
        for x in c:
            if isinstance(x, list) and x[0] == 'property':
                v = get(x, 'value')
                props[get(x, 'name')[1]] = v[1] if v and len(v) > 1 else ''
        fields = []
        fl = get(c, 'fields')
        for x in (fl[1:] if fl else []):
            fields.append((get(x, 'name')[1], x[2] if len(x) > 2 else ''))
        comps[ref] = dict(
            value=get(c, 'value')[1],
            fp=(get(c, 'footprint') or [None, ''])[1],
            datasheet=(get(c, 'datasheet') or [None, ''])[1],
            description=(get(c, 'description') or [None, ''])[1],
            path=get(sp, 'tstamps')[1] + get(c, 'tstamps')[1],
            sheetname=get(sp, 'names')[1],
            sheetfile=props.get('Sheetfile', ''),
            fields=[(n, v) for n, v in fields if n not in ('Footprint', 'Datasheet', 'Description')],
            dnp='dnp' in props,
            excl_bom='exclude_from_bom' in props,
            excl_board='exclude_from_board' in props,
        )
    nets = {}
    for n in get(d, 'nets')[1:]:
        name = get(n, 'name')[1]
        for x in n:
            if isinstance(x, list) and x[0] == 'node':
                nets[(get(x, 'ref')[1], get(x, 'pin')[1])] = name
    return comps, nets


def ler_fp_lib_table(pcb_dir):
    libs = {}
    t = open(os.path.join(pcb_dir, 'fp-lib-table'), encoding='utf8').read()
    for name, uri in re.findall(r'\(lib \(name "([^"]+)"\)\(type "[^"]+"\)\(uri "([^"]+)"\)', t):
        libs[name] = uri.replace('${KIPRJMOD}', pcb_dir).replace('/', os.sep)
    return libs


def campos(fp):
    return {f.GetName(): f for f in fp.GetFields()}


def novo_campo(fp, nome, texto, modelo):
    f = pcbnew.PCB_FIELD(fp, pcbnew.FIELD_T_USER, nome)
    if hasattr(f, 'SetOrdinal'):
        f.SetOrdinal(fp.GetNextFieldOrdinal())
    if modelo is not None:
        f.SetAttributes(modelo, False)
        f.SetLayer(modelo.GetLayer() if fp.GetLayer() == pcbnew.F_Cu else pcbnew.B_Fab)
    else:
        f.SetLayer(pcbnew.F_Fab if fp.GetLayer() == pcbnew.F_Cu else pcbnew.B_Fab)
        f.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.0)))
        f.SetTextThickness(pcbnew.FromMM(0.15))
    f.SetVisible(False)
    f.SetPosition(fp.GetPosition())
    f.SetText(texto)
    fp.Add(f)
    return f


def pads_por_numero(fp):
    d = collections.defaultdict(list)
    for p in fp.Pads():
        if p.GetNumber():
            d[p.GetNumber()].append(p.GetPosition())
    return d


def custo_orientacao(old, new):
    """Soma, por número de pad, da distância do pad novo ao pad antigo mais próximo com o mesmo número."""
    po, pn = pads_por_numero(old), pads_por_numero(new)
    tot = 0.0
    for num, lst in pn.items():
        if num not in po:
            continue
        for q in lst:
            tot += min(((q.x - o.x) ** 2 + (q.y - o.y) ** 2) ** 0.5 for o in po[num])
    return pcbnew.ToMM(int(tot))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    pcb_in, net_fn, pcb_out = args
    pcb_dir = os.path.dirname(os.path.abspath(pcb_in))
    libs = ler_fp_lib_table(pcb_dir)
    comps, nets = ler_netlist(net_fn)
    comps = collections.OrderedDict((r, c) for r, c in comps.items() if not c['excl_board'])

    b = pcbnew.LoadBoard(pcb_in)
    mm = pcbnew.ToMM
    log = collections.defaultdict(list)

    # ---------- 1. ligação símbolo <-> footprint
    by_path = {f.GetPath().AsString(): f for f in b.GetFootprints()}
    by_ref = {f.GetReference(): f for f in b.GetFootprints()}
    comp_paths = {c['path'] for c in comps.values()}
    match = {}
    for r, c in comps.items():
        f = by_path.get(c['path'])
        if f is None:
            g = by_ref.get(r)
            if g is not None and g.GetPath().AsString() not in comp_paths:
                f = g
                log['religados'].append(f"{r}: {g.GetPath().AsString()} ({g.GetSheetname() or '-'}) -> {c['path']} ({c['sheetname']})")
        if f is not None:
            match[r] = f
    # id() dos objectos SWIG muda a cada GetFootprints(): a identidade tem de ser o UUID do footprint
    matched_ids = {f.m_Uuid.AsString() for f in match.values()}
    extras = sorted((f for f in b.GetFootprints() if f.m_Uuid.AsString() not in matched_ids),
                    key=lambda f: natkey(f.GetReference()))
    novos = [r for r in comps if r not in match]
    if len(extras) + len(match) != len(b.GetFootprints()):
        raise SystemExit('ligação inconsistente: footprints ligados + a apagar != footprints na placa')

    # ---------- 2. apagar footprints sem símbolo
    for f in extras:
        log['apagados'].append(f"{f.GetReference()} {f.GetFPID().GetUniStringLibId()} ({mm(f.GetPosition().x):.3f}, {mm(f.GetPosition().y):.3f})")
        if not dry:
            b.Remove(f)

    # modelos de estilo para campos de utilizador (o primeiro footprint da placa que tenha o campo)
    modelo_campo = {}
    for f in b.GetFootprints():
        for n, fld in campos(f).items():
            modelo_campo.setdefault(n, fld)

    # ---------- 3. substituir footprints
    substituidos = set()
    for r, f in list(match.items()):
        c = comps[r]
        if not c['fp'] or f.GetFPID().GetUniStringLibId() == c['fp']:
            continue
        nick, name = c['fp'].split(':', 1)
        new = pcbnew.FootprintLoad(libs[nick], name)
        if new is None:
            raise SystemExit(f'footprint {c["fp"]} não encontrado em {libs[nick]}')
        new.SetFPID(pcbnew.LIB_ID(nick, name))
        if f.IsFlipped():
            new.Flip(new.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        new.SetPosition(f.GetPosition())
        theta = f.GetOrientationDegrees()
        custos = {}
        for cand in (theta, (theta + 180.0) % 360.0):
            new.SetOrientationDegrees(cand)
            custos[cand] = custo_orientacao(f, new)
        melhor = min(custos, key=lambda k: (round(custos[k], 3), k != theta))
        new.SetOrientationDegrees(melhor)
        new.SetLocked(f.IsLocked())
        new.SetReference(f.GetReference())
        new.SetPath(f.GetPath())
        new.SetSheetname(f.GetSheetname())
        new.SetSheetfile(f.GetSheetfile())
        ov = {}
        for attr in ('LocalClearance', 'LocalSolderMaskMargin', 'LocalSolderPasteMargin', 'LocalZoneConnection'):
            v = getattr(f, 'Get' + attr)()
            ov[attr] = v
            herdado = v is None or (attr == 'LocalZoneConnection' and v == pcbnew.ZONE_CONNECTION_INHERITED)
            if not herdado:
                getattr(new, 'Set' + attr)(v)
                log['avisos'].append(f'{r}: copiado {attr} = {v}')
        log['overrides'].append(f'{r}: {ov}')
        # textos: a mesma posição absoluta, camada e estilo que tinham
        nf = campos(new)
        for n, of in campos(f).items():
            g = nf.get(n)
            if g is None:
                g = pcbnew.PCB_FIELD(new, pcbnew.FIELD_T_USER, n)
                if hasattr(g, 'SetOrdinal'):
                    g.SetOrdinal(new.GetNextFieldOrdinal())
                new.Add(g)
            g.SetAttributes(of, True)
            g.SetLayer(of.GetLayer())
            g.SetVisible(of.IsVisible())   # no KiCad 10 o SetAttributes não copia a visibilidade
            g.SetText(of.GetText())
        log['substituidos'].append(f"{r}: {f.GetFPID().GetUniStringLibId()} -> {c['fp']} em ({mm(f.GetPosition().x):.3f}, {mm(f.GetPosition().y):.3f}); "
                                   f"rot {theta:g} -> {melhor:g} (desvio dos pads por número: " +
                                   ', '.join(f'{k:g}°={v:.3f} mm' for k, v in custos.items()) + ')')
        if not dry:
            b.Remove(f)
            b.Add(new)
        match[r] = new
        substituidos.add(r)

    # ---------- 4. footprints novos, estacionados abaixo da placa
    # grupos: footprints novos ligados por redes locais (até 6 pinos no esquemático; ex.: um canal).
    # Redes maiores (GND_ADC, +24V_ADC, VZ_LIM) não agrupam.
    novos_set = set(novos)
    npinos = collections.Counter(nets.values())
    par = {r: r for r in novos}

    def raiz(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    membros = collections.defaultdict(set)
    for (ref, pin), n in nets.items():
        if ref in novos_set:
            membros[n].add(ref)
    for n, ms in membros.items():
        if len(ms) >= 2 and npinos[n] <= 6:
            ms = sorted(ms)
            for m in ms[1:]:
                par[raiz(m)] = raiz(ms[0])
    grupos = collections.defaultdict(list)
    for r in novos:
        grupos[raiz(r)].append(r)
    grupos = [sorted(g, key=natkey) for g in grupos.values()]
    multi = sorted([g for g in grupos if len(g) > 1], key=lambda g: natkey(g[0]))
    soltos = sorted([g[0] for g in grupos if len(g) == 1], key=natkey)
    linhas = multi + ([soltos] if soltos else [])
    bb = b.GetBoardEdgesBoundingBox()
    x0 = bb.GetX() + pcbnew.FromMM(6)
    y0 = bb.GetBottom() + pcbnew.FromMM(10)
    passo = pcbnew.FromMM(9)
    for i, linha in enumerate(linhas):
        for j, r in enumerate(linha):
            c = comps[r]
            nick, name = c['fp'].split(':', 1)
            new = pcbnew.FootprintLoad(libs[nick], name)
            if new is None:
                raise SystemExit(f'footprint {c["fp"]} não encontrado em {libs[nick]}')
            new.SetFPID(pcbnew.LIB_ID(nick, name))
            new.SetReference(r)
            new.SetPath(pcbnew.KIID_PATH(c['path']))
            new.SetSheetname(c['sheetname'])
            new.SetSheetfile(c['sheetfile'])
            new.SetPosition(pcbnew.VECTOR2I(x0 + j * passo, y0 + i * passo))
            new.SetOrientationDegrees(0)
            log['novos'].append(f"{r} {c['fp']} estacionado em ({mm(x0 + j * passo):.1f}, {mm(y0 + i * passo):.1f})")
            if not dry:
                b.Add(new)
            match[r] = new

    # ---------- 5. valores, campos, path, folha e atributos
    for r, f in match.items():
        c = comps[r]
        if f.GetPath().AsString() != c['path']:
            f.SetPath(pcbnew.KIID_PATH(c['path']))
        if f.GetSheetname() != c['sheetname']:
            f.SetSheetname(c['sheetname'])
        if f.GetSheetfile() != c['sheetfile']:
            f.SetSheetfile(c['sheetfile'])
        if f.GetValue() != c['value']:
            log['valores'].append(f"{r}: {f.GetValue()} -> {c['value']}")
            f.SetValue(c['value'])
        cf = campos(f)
        if r in substituidos or r in novos_set:
            for n, v in (('Datasheet', c['datasheet']), ('Description', c['description'])):
                if n in cf and cf[n].GetText() != v:
                    cf[n].SetText(v)
        for n, v in c['fields']:
            if n in cf:
                if cf[n].GetText() != v:
                    log['campos'].append(f"{r}.{n}: {cf[n].GetText()} -> {v}")
                    cf[n].SetText(v)
            else:
                novo_campo(f, n, v, modelo_campo.get(n))
                if r not in novos_set:
                    log['campos'].append(f"{r}.{n}: (novo) {v}")
        if f.IsDNP() != c['dnp']:
            log['campos'].append(f"{r}: DNP {f.IsDNP()} -> {c['dnp']}")
            f.SetDNP(c['dnp'])
        if f.IsExcludedFromBOM() != c['excl_bom']:
            log['campos'].append(f"{r}: fora da BOM {f.IsExcludedFromBOM()} -> {c['excl_bom']}")
            f.SetExcludedFromBOM(c['excl_bom'])

    # ---------- 6. redes dos pads
    netinfo = {}

    def rede(nome):
        if nome not in netinfo:
            ni = b.FindNet(nome)
            if ni is None:
                ni = pcbnew.NETINFO_ITEM(b, nome)
                if not dry:
                    b.Add(ni)
                log['redes_novas'].append(nome)
            netinfo[nome] = ni
        return netinfo[nome]

    trocas = collections.defaultdict(set)   # rede antiga -> redes novas (pads que ficam)
    for r, f in match.items():
        for p in f.Pads():
            num = p.GetNumber()
            if not num:
                continue
            alvo = nets.get((r, num))
            antes = p.GetNetname()
            if alvo is None:
                if antes:
                    log['avisos'].append(f'{r}.{num}: pad sem nó no netlist (fica em {antes})')
                continue
            if alvo != antes:
                if r not in novos_set and r not in substituidos:
                    log['pads'].append(f'{r}.{num}: {antes} -> {alvo}')
                    trocas[antes].add(alvo)
                ni = rede(alvo)
                if not dry:
                    p.SetNet(ni)

    # pads que ficam em cada rede depois da actualização
    pads_depois = collections.Counter()
    for r, f in match.items():
        for p in f.Pads():
            n = nets.get((r, p.GetNumber()), p.GetNetname())
            pads_depois[n] += 1

    # ---------- 7. pistas, vias e zonas de redes renomeadas
    for antiga, novas in sorted(trocas.items()):
        if len(novas) == 1 and pads_depois[antiga] == 0:
            nova = next(iter(novas))
            nt = nz = 0
            for t in b.GetTracks():
                if t.GetNetname() == antiga:
                    nt += 1
                    if not dry:
                        t.SetNet(rede(nova))
            for z in b.Zones():
                if z.GetNetname() == antiga:
                    nz += 1
                    if not dry:
                        z.SetNet(rede(nova))
            log['renomeadas'].append(f'{antiga} -> {nova}: {nt} pistas/vias, {nz} zonas')
        else:
            log['avisos'].append(f'{antiga}: pads foram para {sorted(novas)} e ficam {pads_depois[antiga]}; pistas não mexidas')

    # ---------- 8. pistas que ficam sem pads
    orf = collections.Counter()
    for t in b.GetTracks():
        n = t.GetNetname()
        if n and pads_depois[n] == 0:
            orf[(n, 'via' if t.GetClass() == 'PCB_VIA' else 'pista')] += 1
    for (n, k), v in sorted(orf.items()):
        log['orfas'].append(f'{n}: {v} {k}s sem nenhum pad na rede')

    for k in ('religados', 'apagados', 'substituidos', 'overrides', 'novos', 'valores', 'campos', 'pads', 'redes_novas',
              'renomeadas', 'orfas', 'avisos'):
        print(f'== {k} ({len(log[k])})')
        for s in log[k]:
            print('   ', s)

    if dry:
        print('\n[dry-run] nada gravado')
        return
    b.Save(pcb_out)
    print('\ngravado em', pcb_out)


if __name__ == '__main__':
    main()
