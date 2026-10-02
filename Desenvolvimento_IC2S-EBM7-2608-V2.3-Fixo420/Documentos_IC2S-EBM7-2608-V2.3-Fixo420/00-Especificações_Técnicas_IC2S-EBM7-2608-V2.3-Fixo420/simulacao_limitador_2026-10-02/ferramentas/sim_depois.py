"""
Simulacao do canal de laco 1 tal como ficou no esquematico editado (rama lacos-limitador-discreto).
Os valores saem do netlist exportado (depois.net): R40 (RS), R44 (RG), R48 (RZ), D26 (zener), R13 (burden), R18, C27,
F4 e o TVS D6. A topologia ja foi verificada no verificar_limitador.py (redes com os membros exactos).
Modelos: se parts.json trouxer 'spice' (modelo do fabricante) para o MOSFET/NPN usa-o; senao, modelos genericos
ajustados aos valores das folhas de dados (VGS(th), RDS(on), VBE) -- isso fica dito na saida.
"""
import os, re, sys, json, subprocess
sys.path.insert(0, r'C:\Users\Javier Rivadineira\.claude\jobs\ef5da2a8\tmp')
sys.path.insert(0, r'C:\Users\Javier Rivadineira\.claude\jobs\ef5da2a8\tmp\sem_efuse')
import parse as px
import sim_lazo_com_sem_tps as base

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, 'parts.json'), encoding='utf8'))
comps, nets = px.load(os.path.join(HERE, 'depois.net'))


def val(ref):
    """'3k3' -> 3300, '18R' -> 18, '100k' -> 1e5, '100nF/50V' -> 1e-7 (a letra no meio e a virgula decimal)."""
    v = comps[ref][0].split('/')[0].replace(',', '.')
    m = re.match(r'(\d+)(?:\.(\d+))?\s*([kKMRrmunp]?)(\d*)', v)
    a, frac, suf, b = m.group(1), m.group(2) or '', m.group(3), m.group(4)
    num = float(a + '.' + (frac or b or '0'))
    mult = {'k': 1e3, 'K': 1e3, 'M': 1e6, 'R': 1, 'r': 1, 'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12, '': 1}[suf]
    if v.endswith('F') and suf in ('u', 'n', 'p'):
        return num * mult
    return num * mult


RS, RG, RZ, RB, R18 = val('R40'), val('R44'), val('R48'), val('R13'), val('R18')
C27 = val('C27')
VZ = P['DZ']['vz']
print(f'do netlist: RS {RS} ohm, RG {RG} ohm, RZ {RZ} ohm, burden {RB} ohm, R18 {R18} ohm, C27 {C27} F, zener {comps["D26"][0]} ({VZ} V), '
      f'TVS {comps["D6"][0]}, MOSFET {comps["Q1"][0]}, NPN {comps["Q5"][0]}')

MODELS = base.MOD
inc = ''
RTH_CA = float(os.environ.get('RTH_CA', '90'))     # K/W: RthJA max - RthJS max (BSP297 Rev.2.2 p.2): 115-25 (pegada minima) ou 70-25=45 (6 cm2)
NL = chr(10)
inc += f'.include "{P["MOS"]["spice"]}"' + NL + f'.include "{P["NPN"]["spice"]}"' + NL
# MOSFET: 'L0' = BSP297_L0 da Infineon (nivel 3, robusto); 'TH' = BSP297 completo com nos termicos (Tj, Tcase)
MOS_LINES = {'L0': 'XM1 d1 g1 sx BSP297_L0' + NL + 'VTJ tj 0 0',
             'TH': 'XM1 d1 g1 sx tj tc BSP297' + NL + f'RTHCA tc ta {RTH_CA}'}
# NPN: 'full' = subcircuito Nexperia BC847C (nos 1=C 2=B 3=E); 'core' = so o transistor principal do mesmo modelo
NPN_LINES = {'full': 'XQ2 g1 sx o BC847C', 'core': 'Q2 g1 sx o BC847C_CORE'}
MODELS += """
.model BC847C_CORE NPN(IS=1.641E-014 NF=0.9969 ISE=1.151E-016 NE=1.208 BF=509 IKF=0.0863 VAF=66.64 NR=0.9953
+ ISC=1.068E-014 NC=1.357 BR=9.832 IKR=0.1524 VAR=25 RB=360 IRB=2.5E-005 RBM=0.8 RE=0.6403 RC=0.5461 XTB=1.595
+ EG=1.11 XTI=6.27 CJE=1.119E-011 VJE=0.6755 MJE=0.3391 TF=5.25E-010 XTF=22.74 VTF=2 ITF=0.368 PTF=0
+ CJC=3.693E-012 VJC=0.5083 MJC=0.3642 XCJC=1 TR=0.0008 FC=0.9552)
"""
gm = P['MOS']['generic']; gn = P['NPN']['generic']
MODELS += f"""
.model NMG NMOS(LEVEL=1 VTO={gm['vto']} KP={gm['kp']} LAMBDA=0.002 RD={gm['rd']} RS=0.2 CGSO=4e-9 CGDO=1e-9)
.model NPNG NPN(IS={gn['is']} BF={gn['bf']} VAF=100 CJE=8p CJC=4p TF=0.4n)
.model DZG D(IS=1e-12 N=1.2 BV={VZ} IBV=5m RS=10 CJO=50p)
.model DBODY D(IS=1e-12 N=1.3 RS=0.05 CJO=100p)
"""


def canal(vbus=24.0, itx='20m', extra='', burden=True, mos='L0', npn='full'):
    mos_line, npn_line = MOS_LINES[mos], NPN_LINES[npn]
    s = f"""{inc}
VTA ta 0 {{TAMB}}
VBUS b 0 {vbus - 0.5}
RB b v24 0.3
C24 v24 0 30u
VIF4 v24 f4 0
RF4 f4 s 2.0
D10 0 s T36
RCS s xp {base.RC}
DTX xp xq DTX
ITX xq xn {itx}
CTX xp xn 100n
RCR xn ain {base.RC}
D6 0 ain T36
RZ v24 vz {RZ}
DZ 0 vz DZG
CZ vz 0 100n
RG vz g1 {RG}
VIM1 ain d1 0
{mos_line}
RSENSE sx o {RS}
{npn_line}
VIR13 o o2 0
R13 o2 0 {RB if burden else 1e9}
RFB o adcf 0.1
VIR18 adcf r18 0
R18 r18 aadc {R18}
C27 aadc 0 {C27}
D14a 0 aadc BAV
D14b aadc v33 BAV
VLDO l 0 3.3
DLDO l l2 DI
RLDO l2 v33 0.05
C33 v33 0 15u
RL33 v33 0 660
BTL v33 0 I = 0.001 + max(0, V(v33)-3.6)/0.2
"""
    return s + extra


def op(tag, body, temp=27):
    body = body.replace('{TAMB}', str(temp))
    net = f"* {tag}\n{MODELS}\n{body}\n.temp {temp}\n.options rshunt=1e10\n.control\nop\nprint i(vir13) i(vir18) i(vim1) v(ain) v(sx) v(o) v(aadc) v(g1) v(vz) v(xp) v(xn) v(tj)\n.endc\n.end\n"
    fn = os.path.join(HERE, 'sim_' + re.sub(r'\W+', '_', tag) + f'_{temp}.cir'); open(fn, 'w').write(net)
    t = subprocess.run([base.NG, '-b', fn], capture_output=True, text=True, timeout=120); t = t.stdout + t.stderr
    open(fn[:-4] + '.log', 'w').write(t)
    g = lambda k: float(re.findall(r'^\s*' + re.escape(k) + r'\s*=\s*([-+0-9.eE]+)', t, re.M | re.I)[-1])
    ib, im = g('i(vir13)'), g('i(vim1)')
    return dict(ib=ib, pb=ib * ib * RB, pm=(g('v(ain)') - g('v(sx)')) * im, vo=g('v(o)'), vadc=g('v(aadc)'), i18=g('i(vir18)'),
                vtx=g('v(xp)') - g('v(xn)'), vg=g('v(g1)'), vz=g('v(vz)'), tj=g('v(tj)'))


def tran(tag, body):
    body = body.replace('{TAMB}', '27')
    meas = """let p13=i(vir13)*i(vir13)*{rb}
meas tran p13max max p13
let e13=integ(p13)
meas tran e13f find e13 at=300u
meas tran vadx max v(aadc)
meas tran vadn min v(aadc)
let vds=v(ain)-v(sx)
meas tran vdsx max vds
let pm=vds*i(vim1)
meas tran pmx max pm
meas tran vinx max v(ain)
meas tran vinn min v(ain)
""".replace('{rb}', str(RB))
    net = f"* {tag}\n{MODELS}\n{body}\n.options method=gear reltol=1e-4 itl4=500 rshunt=1e10\n.control\ntran 20n 300u\n{meas}.endc\n.end\n"
    fn = os.path.join(HERE, 'sim_' + re.sub(r'\W+', '_', tag) + '.cir'); open(fn, 'w').write(net)
    t = subprocess.run([base.NG, '-b', fn], capture_output=True, text=True, timeout=600); t = t.stdout + t.stderr
    open(fn[:-4] + '.log', 'w').write(t)
    r = {}
    for k in ('p13max', 'e13f', 'vadx', 'vadn', 'vdsx', 'pmx', 'vinx', 'vinn'):
        m = re.findall(r'^\s*' + k + r'\s*=\s*([-+0-9.eE]+)', t, re.M | re.I); r[k] = float(m[-1]) if m else float('nan')
    return r


if __name__ == '__main__':
    res = {}
    print('--- normal, 20 mA')
    for vb in (18.0, 24.0, 32.0):
        r = op(f'normal bus {vb:.0f}', canal(vbus=vb)); res[f'normal_{vb}'] = r
        print(f"bus {vb:4.0f} V: burden {r['ib']*1e3:6.2f} mA | V no transmissor {r['vtx']:5.2f} V | porta {r['vg']:5.2f} V | VZ {r['vz']:5.2f} V")
    print('--- falhas mantidas')
    for nome, kw, sc in [('transmissor em curto bus 32', dict(vbus=32.0), 'RSC xp xn 0.05\n'),
                         ('AIN a 32 V externo', dict(), 'VEXT ext 0 32\nREXT ext ain 0.2\n'),
                         ('AIN a 32 V externo burden aberta', dict(burden=False), 'VEXT ext 0 32\nREXT ext ain 0.2\n')]:
        for temp in (-40, 27, 60, 85):
            r = op(nome, canal(extra=sc, **kw), temp); res[f'{nome}_{temp}'] = r
            tj115, tj70 = temp + r['pm'] * 115, temp + r['pm'] * 70     # RthJA max BSP297 Rev.2.2 p.2
            print(f"{nome:34s} {temp:4d} C: burden {r['ib']*1e3:6.2f} mA {r['pb']*1e3:6.1f} mW | MOSFET {r['pm']:5.2f} W "
                  f"(Tj {tj115:5.0f} C pegada minima / {tj70:5.0f} C 6 cm2) | no burden {r['vo']:5.2f} V | "
                  f"I(R18) {r['i18']*1e3:5.2f} mA AIN_ADC {r['vadc']:4.2f} V")
    print('--- contraste: modelo Infineon completo com nos termicos (RthCA = 90 K/W, pegada minima)')
    for temp in (-40, 27, 60):
        r = op('curto com modelo termico', canal(vbus=32.0, extra='RSC xp xn 0.05\n', mos='TH'), temp); res[f'termico_{temp}'] = r
        print(f"transmissor em curto bus 32, modelo termico, {temp:4d} C: burden {r['ib']*1e3:6.2f} mA | MOSFET {r['pm']:5.2f} W | Tj simulada {r['tj']:6.1f} C")
    print('--- surto 1 kV em P2.7')
    for pol in (1, -1):
        sg = f"BSG sg 0 V = {1000*pol}*1.037*(exp(-time/68.2u)-exp(-time/0.405u))\nRSG sg sg2 2\nRCDN sg2 sg3 40\nCCDN sg3 ain 0.5u\n"
        r = tran(f'surto {"positivo" if pol > 0 else "negativo"}', canal(itx='12m', extra=sg, npn='core')); res[f'surto_{pol}'] = r
        print(f"{'+' if pol > 0 else '-'}1 kV: P2.7 {r['vinn']:+6.1f}/{r['vinx']:+6.1f} V | Vds max {r['vdsx']:5.1f} V | P MOSFET pico {r['pmx']:5.2f} W | "
              f"burden pico {r['p13max']:6.3f} W E {r['e13f']*1e3:6.3f} mJ | AIN_ADC {r['vadn']:+5.2f}/{r['vadx']:+5.2f} V")
    json.dump(res, open(os.path.join(HERE, 'resultados_sim_depois.json'), 'w'), indent=1)
