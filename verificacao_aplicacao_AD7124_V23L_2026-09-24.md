# Verificação de aplicação — AD7124-8 (U6), EBM7 V2.3 legacy

**Placa:** `IC2S_Extension_Board_Model_7-EBM7-2608_V23L_Load_Cell_4AI` (PCB de 2026-09-23 12:09; netlist exportada do esquemático).
**Procedimento:** skill `2shw-pcb:verificar-aplicacao-datasheet`; linhas avaliadas por `tabela.py` (não escritas à mão), 47 linhas.
**Configuração de software:** a actual é a descrita pelo Rodrigo em 24-09 (V2.2: referência AVDD, todos os buffers ligados, AINM = DGND,
ganho 1 nos laços e 128 na célula, SINC3, SCLK 1 MHz modo 3); a proposta é a da resposta enviada a 24-09.

## 1. CIs e PDFs usados

| CI | PDF | Páginas |
|---|---|---|
| AD7124-8 (U6) | `AnalogDevices_AD7124-8_RevF.pdf` (Rev F) | 7, 8, 9, 10, 11, 14, 16, 17, 47, 73, 75, 89–91 |
| ADR4525 (U7) | `adr4520_4525_4530_4533_4540_4550.pdf` (Rev G, Downloads) | 4, 9, 35 |
| TL431BQ (U4) | `TI_TL431.pdf` | 14 (TL431BQ: Vref 2483–2507 mV, desvio ≤ 34 mV) |
| SPX3819 (U3) | `1016_SPX3819.pdf` | 2 (±1 % a 25 °C, ±2 % em temperatura, 57 ppm/°C) |
| TPS26613 (U8–U11) | `TI_TPS2661x.pdf` (SLVSFE3C) | 5 (IOL 25/32/40 mA) |
| ISO7141 (U5) | `TI_ISO7141CC.pdf` (SLLSE83F) | 8 (tPLH/tPHL ≤ 45 ns a 3,3 V) |
| TVS 824500101 (D20, D21) | `Wurth_824500101.pdf` | 1 (VDC 10 V, VBR 11,7 V ±5 %) |
| NTC NTCS0603E3103JLT (R36) | `Vishay_NTCS0603E3_serie.pdf` | tabela da série (R25 10 kΩ, B25/85 3435 K ±1 %) |

## 2. Tabela

| CI | fonte (§/tabela/nota, pág.) | fórmula | valores usados | resultado | veredito |
|---|---|---|---|---|---|
| AD7124-8 (U6) | Rev F p.9, AVDD-AVSS full power | `2,9 V <= AVDD <= 3,6 V (SPX3819 3,3 V +-2 %, 1016_SPX3819 p.2)` | Vn=3.300, tol=0.02 | Vn*(1-tol) = 3.234 ; Vn*(1+tol) = 3.366 | cumpre |
| AD7124-8 (U6) | Rev F p.9, IOVDD e IOVDD-AVSS | `1,65 <= IOVDD <= 3,6 V e IOVDD-AVSS <= 5,4 V` | Vn=3.300, tol=0.02 | Vn*(1+tol) = 3.366 | cumpre |
| TL431BQ (U4) x AD7124 | TL431 p.14 (Vref 2483-2507 mV, dev <= 34 mV) x AD7124 p.14 (abs max AVDD 3,96 V) | `clamp max = (Vref_max+dev)*(1+R6max/R7min) <= 3,96 V` | Vr=2.507, dev=0.034, R6=4464, R7=9900 | (Vr+dev)*(1+R6/R7) = 3.687 | cumpre |
| TL431BQ (U4) x SPX3819 | TL431 p.14 x SPX3819 p.2 | `clamp min > AVDD max normal (TL431 nao conduz em operacao)` | Vr=2.483, dev=0.034, R6=4376, R7=1.01e+04, Vavdd=3.366 | (Vr-dev)*(1+R6/R7) = 3.510 ; Vavdd = 3.366 | cumpre |
| TL431BQ (U4) x AD7124 | AD7124 p.9 (full power <= 3,6 V) | `clamp max <= 3,6 V (so com o SPX3819 em falha)` | Vr=2.507, dev=0.034, R6=4464, R7=9900 so em falha do regulador; abs max cumprido na linha anterior | (Vr+dev)*(1+R6/R7) = 3.687 | **FALHA** |
| AD7124-8 (U6) | Rev F p.73 | `AVDD: 0,1 uF encostado ao chip (C15 -> pino 26, mm)` | d=1.550 limiar 2,0 mm = criterio D (o datasheet nao da numero) | d = 1.550 | cumpre |
| AD7124-8 (U6) | Rev F p.73 | `AVDD: 1 uF tantalo || 0,1 uF (bulk, uF)` | C=10.000 C14 e MLCC 10 uF, nao tantalo: desvio de tipo, nao de valor | C = 10.000 | cumpre |
| AD7124-8 (U6) | Rev F p.73 | `IOVDD: 0,1 uF encostado ao chip (C16 -> pino 2, mm)` | d=2.760 limiar 2,0 mm = criterio D; C16 e NFM passante com 3 furos GND proprios | d = 2.760 | **FALHA** |
| AD7124-8 (U6) | Rev F p.73 | `IOVDD: 1 uF || 0,1 uF (bulk, uF)` | C=10.000 | C = 10.000 | cumpre |
| AD7124-8 (U6) | Rev F p.16 e p.73 | `REGCAPA e REGCAPD: 0,1 uF cada (C20, C19)` | Ca=0.1, Cd=0.1 | Ca = 0.1 ; Cd = 0.1 | cumpre |
| AD7124-8 (U6) | Rev F p.47 | `REFOUT: 0,1 uF obrigatorio com referencia interna activa (C18 100 nF + C21 1 uF)` | C=1.100 | C = 1.100 | cumpre |
| AD7124-8 (U6) | Rev F p.7 (Output Current 10 mA) | `carga do REFOUT (divisor NTC a +85 C) <= 10 mA` | Vr=2.500, Rntc=1451, R37=2.2e+04 | Vr/(Rntc+R37) = 0.0001066 | cumpre |
| AD7124-8 (U6) | Rev F p.73 (All analog inputs must be decoupled to AVSS) | `condensadores de AIN8/AIN9 a AVSS` | n=0 so C48 10 nF diferencial AIN8-AIN9; nenhum a AVSS | n = 0 | **FALHA** |
| AD7124-8 (U6) | Rev F p.73 (decouple the REFINx(+) ... to AVSS) | `REFIN1+: C39; REFIN2+: C24, C25` | n1=1.000, n2=2.000 | n1 = 1.000 ; n2 = 2.000 | cumpre |
| AD7124-8 (U6) | Rev F p.7 (External REFIN 0,5...AVDD) | `REFIN2 = ADR4525 2,5 V dentro de 0,5...AVDD` | V=2.500, Avdd=3.234 | V = 2.500 | cumpre |
| AD7124-8 (U6) | Rev F p.7 (buffered AVSS+0,1...AVDD-0,1) | `REFIN2(+) bufferizado: 2,5 V <= AVDD_min - 0,1` | V=2.500, Avdd=3.234 | Avdd-0.1 = 3.134 | cumpre |
| AD7124-8 (U6) | Rev F p.7 / p.47 (buffers pedem 100 mV) | `REFINx(-) = 0 V com REF_BUFM = 1 (config. actual do Pi: todos os buffers ligados)` | Vm=0 config. actual do software (Rodrigo 24-09) | Vm = 0 | **FALHA** |
| AD7124-8 (U6) | Rev F p.7 (unbuffered AVSS-0,05) | `REFINx(-) = 0 V com REF_BUFM = 0 (config. proposta)` | Vm=0 | Vm = 0 | cumpre |
| AD7124-8 (U6) | Rev F p.16 (REFIN1(+) >= AVSS+0,5) e p.8 (REF_DET < 0,7 V) | `REFIN1 pior caso (H1 = 2V5, Vf D23 = 0,7 V): Vb/2 >= 0,7 V` | Vs=2.500, Vf=0.7, Rb=350.000, R30=68.000 Vf do RB162MM-60 [FD]: datasheet ausente; 0,7 V e pessimista; ponte 350 ohm (RF1) | (Vs-Vf)/(Rb+R30)*Rb/2 = 0.7536 | cumpre |
| AD7124-8 (U6) | Rev F p.7 (buffered <= AVDD-0,1) | `REFIN1 melhor caso (H1 = 5 V, Vf = 0): Vb/2 <= AVDD_min - 0,1` | Vs=5.000, Vf=0, Rb=350.000, R30=68.000, Avdd=3.234 | (Vs-Vf)/(Rb+R30)*Rb/2 = 2.093 | cumpre |
| AD7124-8 (U6) | Rev F p.8 (unbuffered ref +-12 uA) x RF1 (erro < 0,5 %) | `REFIN1 sem buffer: 12 uA x (R28||R29) / REFIN1 < 0,5 %` | I=1.2e-05, R=5000, Vref=1.930 exige REF_BUFP = 1 no canal da celula | I*R/Vref = 0.03109 | **FALHA** |
| AD7124-8 (U6) | Rev F p.7 (buffered ref +-3 nA full power) | `REFIN1 com buffer: 3 nA x 5 kohm / REFIN1 < 0,5 %` | I=3e-09, R=5000, Vref=1.930 | I*R/Vref = 7.772e-06 | cumpre |
| AD7124-8 (U6) | Rev F p.7 (+-VREF/gain) | `laco: 20 mA x 110 ohm <= VREF2 = 2,5 V` | I=0.02, Rb=110.000, Vref=2.500 | I*Rb = 2.200 | cumpre |
| AD7124-8 (U6) | Rev F p.7 (G = 1 buffered 0,1...AVDD-0,1) | `laco AINP: 4...22,7 mA x 110 ohm dentro de 0,1...AVDD_min-0,1` | Rb=110.000, Avdd=3.234 | 0.004*Rb = 0.44 ; Avdd-0.1 = 3.134 | cumpre |
| AD7124-8 (U6) | Rev F p.7 | `laco AINM = AVSS/DGND (0 V) com AIN_BUFM = 1 (config. actual)` | Vm=0 config. actual do software | Vm = 0 | **FALHA** |
| AD7124-8 (U6) | Rev F p.7 (G = 1 unbuffered -0,05...) | `laco AINM = 0 V com AIN_BUFM = 0 (config. proposta)` | Vm=0 | Vm = 0 | cumpre |
| AD7124-8 (U6) | Rev F p.7 (unbuffered +-2,65 uA/V) x RF2 (< 0,2 %) | `laco AINP sem buffer: 2,65 uA/V x 2,2 V x R18 3k3 / 2,2 V < 0,2 %` | k=2.65e-06, V=2.200, R=3300 exige AIN_BUFP = 1 | k*V*R = 0.01924 | **FALHA** |
| AD7124-8 (U6) | Rev F p.7 (buffered +-3,3 nA full power) | `laco AINP com buffer: 3,3 nA x 3k3 / 2,2 V < 0,2 %` | I=3.3e-09, R=3300, V=2.200 | I*R = 1.089e-05 | cumpre |
| AD7124 x TPS26613 | AD7124 p.14 (AIN <= AVDD+0,3) x TPS2661x p.5 (IOL max 40 mA) | `falha: IOL_max x 110 ohm <= AVDD + 0,3 V` | I=0.04, Rb=110.000, Avdd=3.300 so com transmissor em curto e IOL > 32,7 mA | I*Rb = 4.400 | **FALHA** |
| AD7124 x TPS26613 | AD7124 p.14 (AINx input current 10 mA) | `falha: corrente no pino <= (4,4 - 3,3) / R18 <= 10 mA` | V=4.400, Avdd=3.300, R=3300 | (V-Avdd)/R = 0.0003333 | cumpre |
| AD7124-8 (U6) | Rev F p.75 (antialias obrigatorio; sem numero) | `laco: fc = 1/(2 pi R18 C27) <= f_mod/100` | R=3300, C=1e-07, fmod=6.144e+05 limiar /100 = criterio D | 1/(2*pi*R*C) = 482.288 | cumpre |
| AD7124-8 (U6) | Rev F p.7 (+-VREF/gain) x celula | `celula: S x Vb <= REFIN1/128 = (Vb/2)/128  (S em V/V)` | S=?, ratio=0.5 falta a sensibilidade da celula; com 2 mV/V usa 51 % da escala | missing: S | **falta dado** |
| AD7124-8 (U6) | Rev F p.7 (G > 1: AVSS-0,05...AVDD+0,05) | `celula: modo comum Vb/2 (H1 = 5 V) dentro de -0,05...AVDD+0,05` | Vcm=1.930, Avdd=3.234 | Vcm = 1.930 | cumpre |
| AD7124-8 (U6) | Rev F p.75 | `celula: fc diferencial = 1/(2 pi 2x1k3 (C46+C43/2)) <= f_mod/100` | R=1300, Cd=2.2e-06, Cc=1e-07, fmod=6.144e+05 | 1/(2*pi*2*R*(Cd+Cc/2)) = 27.206 | cumpre |
| AD7124 x TVS 824500101 | AD7124 p.14 x Wurth 824500101 p.1 (VBR 11,7 V +-5 %) | `celula ligada a 24 V por engano: V_TVS <= AVDD+0,3` | Vt=12.285, Avdd=3.300 o pino fica acima de AVDD+0,3 enquanto o BAV199 conduz; so em falha de cablagem | Vt = 12.285 | **FALHA** |
| AD7124 x TVS 824500101 | AD7124 p.14 (10 mA) | `idem: corrente maxima possivel no pino, sem contar o BAV199, <= 10 mA` | Vt=12.285, Avdd=3.300, R=1300 | (Vt-Avdd)/R = 0.006912 | cumpre |
| AD7124-8 (U6) | Rev F p.7 x escopo RF3 (-40...+85 C) | `NTC: V_AIN9 de -40 a +85 C dentro de 0,1...AVDD-0,1 (B = 3435 K, Vishay)` | Vlo=0.2035, Vhi=2.345, Avdd=3.234 | Vlo = 0.2035 ; Vhi = 2.345 | cumpre |
| AD7124-8 (U6) | Rev F p.7 (unbuffered +-2,65 uA/V) | `NTC sem buffer: 2,65 uA/V x 2,35 V x 3 kohm / 2,35 V < 0,1 %` | k=2.65e-06, V=2.345, R=3000 exige AIN_BUFP = 1 | k*V*R = 0.01864 | **FALHA** |
| AD7124-8 (U6) | Rev F p.7 x SPX3819 p.2 (57 ppm/C) x RF2 | `lacos com referencia AVDD (config. actual): deriva 57 ppm/C x 40 K < 0,2 %` | tc=5.7e-05, dT=40.000 calibracao por placa nao remove deriva; passar a REFIN2 | tc*dT = 0.00228 | **FALHA** |
| AD7124-8 (U6) | Rev F p.11 (t3, t4 >= 100 ns) | `SCLK 1 MHz: meio periodo >= 100 ns` | f=1e+06 | 0.5/f = 5e-07 | cumpre |
| AD7124 x ISO7141 | AD7124 p.11 (dados validos <= 80 ns) x ISO7141 p.8 (tPLH/tPHL <= 45 ns) | `ida e volta: 2 x 45 + 80 ns <= meio periodo` | tiso=4.5e-08, tv=8e-08, f=1e+06 | 2*tiso+tv = 1.7e-07 | cumpre |
| AD7124-8 (U6) | Rev F p.16 (SYNC baixo mantem o modulador em reset) | `SYNC alto: pull-up R9 10k a IOVDD` | pullup=1.000 | pullup = 1.000 | cumpre |
| AD7124-8 (U6) | Rev F p.17 (Connect the exposed pad to AVSS) | `EP (pino 33) ligado a GND_ADC` | ok=1.000 | ok = 1.000 | cumpre |
| AD7124-8 (U6) | Rev F p.73 (Avoid running digital lines under the device) | `pistas de outras redes sob o U6 (+-2,5 mm)` | n=0 | n = 0 | cumpre |
| AD7124-8 (U6) | Rev F p.73 (Avoid crossover of digital and analog signals) | `cruzamentos SPI x entradas analogicas em camadas diferentes` | n=0 | n = 0 | cumpre |
| ADR4525 (U7) x AD7124 | ADR4525 Rev G p.4 (VIN 3-15 V, dropout 500 mV) | `VIN = +3.3V_ANA min >= 3,0 V` | V=3.234 | V = 3.234 | cumpre |
| ADR4525 (U7) x AD7124 | ADR4525 p.35 Table 11 (C_OUT >= 1 uF) e p.9 (carga 0,1-100 uF) | `1 <= C24 + C25 <= 100 uF` | C=10.100 | C = 10.100 | cumpre |

cumpre: 35 · FALHA: 11 · falta dado: 1


## 3. Leitura dos resultados

As 11 linhas **FALHA** não são todas defeitos de placa. Separam-se em três grupos:

**A. Hardware — achados reais**

1. **AIN8/AIN9 (NTC) sem desacoplo a AVSS.** Rev F p.73: «All analog inputs must be decoupled to AVSS». Só existe C48 (10 nF) entre AIN8 e AIN9;
   o modo comum destas duas entradas não tem filtro. Correcção: um condensador de cada entrada a GND_ADC (ex.: 10 nF 0603), junto ao U6.
   Exige footprints novos → para a próxima revisão ou para a sem_trilhas.
2. **Sobretensão nas entradas em falha.** Com transmissor em curto e IOL acima de 32,7 mA (máx. 40 mA, TPS p.5) o burden chega a 4,4 V; com a
   célula ligada a 24 V por engano o TVS segura ~12,3 V. Nos dois casos o pino passa AVDD + 0,3 V (p.14) enquanto o BAV199 conduz. A corrente
   fica limitada por R18 (0,33 mA) e por R31/R32 (≤ 6,9 mA, dividida com o BAV199), abaixo dos 10 mA de p.14. Violação formal de tensão
   **só em falha**, com corrente dentro do limite.
3. **Clamp do TL431 no pior caso = 3,69 V**, acima dos 3,6 V de operação em full power (p.9), abaixo dos 3,96 V absolutos (p.14). Só actua com o
   SPX3819 avariado; em operação normal o TL431 não conduz (clamp mínimo 3,51 V > 3,37 V).
4. *(critério D)* C16 (0,1 µF do IOVDD) a 2,76 mm do pino; o datasheet diz «ideally right up against the device» sem número. É um NFM com os
   seus próprios furos a GND; observação, não bloqueante.

**B. Requisitos para o software do Raspberry (a configuração actual falha)**

| Registo | Canal | Valor | Linha que o exige |
|---|---|---|---|
| REF_BUFM | todos os que usam REFIN1/REFIN2 | **0** | REFINx(−) = 0 V < AVSS + 0,1 |
| AIN_BUFM | laços e NTC (negativo em AVSS) | **0** | AINM = 0 V < AVSS + 0,1 |
| REF_BUFP | célula (REFIN1) | **1** | sem buffer: 12 µA × 5 kΩ = 60 mV → 3,1 % |
| AIN_BUFP | laços e NTC | **1** | sem buffer: 19 mV → 0,87 % (laços) e 0,8 % (NTC) |
| REF_SEL | laços | **REFIN2** (ADR4525) | com AVDD a deriva do SPX3819 dá 0,23 % em 40 K > 0,2 % |
| REF_SEL | célula | **REFIN1** | ratiometria (RF1) |
| REF_SEL + REF_EN | NTC | **interna**, referência interna activa | o divisor é alimentado pelo REFOUT |

**C. Dado em falta**

- **Sensibilidade da célula de carga (mV/V).** Com 2 mV/V a escala é usada a 51 %; com 3 mV/V a 77 %. Qualquer valor até 3,9 mV/V cabe.

## 4. Teste de uma multiplicação por cadeia analógica

**Laço 4-20 mA** (AI1 → U8 → R10 0 Ω → burden 110 Ω → FB4 → R18 3k3 → AIN4, com C27 100 nF e BAV199):

| Corrente | Burden | Pino (buffer ligado, ±3,3 nA × 3k3 = 11 µV) | Código (REFIN2 2,5 V) |
|---|---|---|---|
| 4 mA | 0,44 V | 0,44 V | 2 952 790 |
| 20 mA | 2,20 V | 2,20 V | 14 763 950 |
| 22,7 mA | 2,50 V | 2,50 V | saturação |
| 40 mA (falha) | 4,40 V | ≈ AVDD + Vf (clamp) | saturação |

**Célula de carga** (H1 → D23 → IEXC2 → R30 68 Ω → IEXC_OUT → ponte 350 Ω; REFIN1 = V_ponte/2 por R28/R29):

| H1 | I_exc (Vf 0,4 V [FD]) | V_ponte | REFIN1 | Fundo de escala (G 128) | Sinal a 2 mV/V |
|---|---|---|---|---|---|
| 5 V | 11,0 mA | 3,85 V | 1,93 V | ±15,0 mV | 7,7 mV (51 %) |
| 3,3 V | 6,9 mA | 2,43 V | 1,21 V | ±9,5 mV | 4,9 mV (51 %) |
| 2,5 V | 5,0 mA | 1,76 V | 0,88 V | ±6,9 mV | 3,5 mV (51 %) |

**NTC** (REFOUT 2,5 V → R36 NTC → nó → R37 22k → GND; nó → R38 3k → AIN9; REFOUT → R39 3k → AIN8):

| Temperatura | R_NTC (B = 3435 K) | V_AIN9 | Corrente no REFOUT |
|---|---|---|---|
| −40 °C | 248 kΩ | 0,20 V | 9 µA |
| +25 °C | 10 kΩ | 1,72 V | 78 µA |
| +85 °C | 1,45 kΩ | 2,35 V | 107 µA |

## 5. O que nenhuma ferramenta viu

- **ERC, DRC e o analisador kicad-happy passam com a configuração actual do software**, que viola p.7 em três registos (REF_BUFM, AIN_BUFM,
  e a escolha de AVDD como referência). Só o cruzamento entre a p.7 do datasheet e a configuração do Rodrigo o mostra.
- A falta de desacoplo a AVSS em AIN8/AIN9 não gera aviso em nenhuma ferramenta: C48 existe e liga às duas entradas.
- As sobretensões em falha dependem de três CIs ao mesmo tempo (TPS26613 IOL máx., burden, abs máx. do AD7124) e de um TVS; nenhuma peça isolada falha.

## 6. Limites desta revisão

- **Não é independente:** feita na mesma sessão que alterou a placa e escreveu a resposta ao Rodrigo.
- Vf do RB162MM-60 (D23) sem datasheet local: assumido 0,4 V (0,7 V no pior caso de REF_DET, que ainda passa com 0,754 V).
- Não cobre: filtros digitais e rejeição 50/60 Hz (dependem da configuração final do software), ruído (tabelas de ruído p.19–20), o sensor de
  temperatura interno, burnout e diagnósticos, e o modelo do cabo de 40 m na medição ratiométrica da célula (4 fios, sem sense).
- Distâncias de desacoplo e o ADR4525 a 10,2 mm do REFIN2 (ADR4525 p.35: «as close to the load as possible») são qualitativas no datasheet;
  os limiares usados são critério D e estão marcados.
