# Perguntas ao firmware — EBM7 V2.3 legacy 4-20 mA

Objectivo: fechar suposições do hardware e confirmar as constantes que **mudam** com esta versão. Prioritárias: 1, 2, 5–8 e 10.

## 1. Configuração actual do AD7124

1. Que referência usa cada canal (REFIN1, REFIN2, interna 2,5 V ou AVDD)? Os laços 4-20 mA medem contra **REFIN2 (ADR4525, 2,5 V)**? O orçamento de exactidão assume que sim.
2. Que referência estava configurada no firmware da **V2.2**? (Na placa, R150/R151/R152 montados punham REFIN2 a 5 V — fora do permitido; ou o firmware usava AVDD?)
3. Por canal: ganho, buffers de entrada e de referência, taxa de saída e filtro (rejeição 50/60 Hz).
4. Mapa de pinos AIN usado — confirmar contra o esquemático: AIN1–AIN4 laços, AIN5/AIN6 célula, AIN8/AIN9 temperatura, REFIN1 ratiométrica.

## 2. Constantes que mudam na legacy

5. Burden: 160 Ω (V2.2) → **110 Ω**.
6. Referência dos laços: **2,5 V (ADR4525)**.
7. Divisor da NTC: 5k62 → **22k (R37)**. Que fórmula/tabela usa a NTC?
8. Célula de carga: medição **ratiométrica** contra REFIN1, série 1k3 + filtro diferencial. A fórmula assume a tensão de excitação ou trabalha em proporção?

## 3. Calibração (decide se RF2 < 0,2 % se cumpre)

9. É feita a calibração interna de zero e fundo de escala no arranque?
10. Há calibração por placa com corrente padrão, guardada em memória? Sem ela o pior caso é 0,30 %; com ela, 0,16 %.
11. Constante comum a todas as placas ou por unidade?

## 4. Diagnóstico e falhas

12. Detecção de laço aberto (< 3,6 mA) e de falha (> 21 mA)? O ADC mede até 22,7 mA.
13. Com transmissor em curto o TPS26613 limita 100 ms e corta 800 ms em ciclo; a leitura pulsa. O firmware filtra ou sinaliza? (SGOOD não está ligado.)
14. Usam REF_DET (REFIN < 0,7 V) ou o registo de erros? Detectariam shunt errado em H1 ou célula desligada.
15. Lêem AVDD, IOVDD ou a referência pelos canais internos para vigiar as alimentações?

## 5. Excitação e comunicação

16. Como sabe o firmware que tensão de excitação o shunt de H1 seleccionou (5 V / 3,3 V / 2,5 V)?
17. Frequência do SCLK do SPI? O ISO7141 acrescenta atraso e limita a velocidade máxima.
18. Usam as fontes de corrente internas ou os GPIO do AD7124 para alguma coisa?

---

## Resposta do Rodrigo (software do Raspberry Pi) — resumo e verificação, 24-09

- **Não há firmware na EBM7**: o software do Pi fala com o AD7124 por SPI (1 MHz, modo 3, sem CRC) e converte para engenharia.
- **V2.2**: todos os canais com referência **AVDD 3,3 V**; REFIN1/REFIN2 não usados; referência interna habilitada. Vetor de fábrica 16.244.633 a 3,2 V → 3,305 V ✔.
  Mas o REFIN2 e o REFOUT estavam ligados ao +5V_ADC por 0 Ω (acima de AVDD + 0,3 V = 3,6 V) → **AD7124 das V2.2 sob suspeita**. Na legacy +2,5_VREF não toca o 5 V e R8 é DNP ✔.
- **Calibração**: 6 pontos (0–20 mA) por unidade e por canal, guardada no Pi → cenário 0,16 % ✔. Sem calibração interna do AD7124.
- **Configuração**: célula ganho 128 bipolar ~400 SPS; laços ganho 1 unipolar ~4800 SPS; SINC3, sem rejeição 50/60 Hz; todos os buffers ligados.
- **Mapa**: AI1 = AIN4 … AI4 = AIN1 — **igual na legacy** (seguido pela netlist: P2.7 → U8 → R10 → FB4 → R18 → AIN1_ADC → pino 8 = AIN4). Negativo dos laços = DGND interno (código 19).
- **Vetor novo** [0; 2.952.790; …; 14.763.950] = I·110/2,5·2²⁴ ✔.
- **NTC não é lida hoje**; RF3 exige-a → função nova.

## Retorno do hardware às perguntas dele

| Tema | Resposta | Fonte |
|---|---|---|
| Buffers em 0 V | laços AIN_BUFP 1 / AIN_BUFM 0, negativo **AVSS (17)**; REFIN2 REF_BUFM 0 (REF_BUFP opcional); **REFIN1 REF_BUFP = 1 obrigatório** (divisor 10k/10k = 5 kΩ × ±12 µA ≈ 60 mV), REF_BUFM 0 | AD7124 p.7, p.8, p.91; netlist (pino 13 REFIN1− e 21 REFIN2− a GND_ADC) |
| Limite superior | NAMUR NE 43: ≤ 3,6 e ≥ 21,0 mA falha; 20,5–21,0 sobre-alcance; saturação 22,7 mA | NE 43; 2,5 V/110 Ω |
| SGOOD | impossível nesta placa (ISO7141 com 4 canais no SPI; GPIO do AD7124 só saídas); detectar por código máximo ~100 ms + ~0 durante 800 ms | TI p.23; decisão 04-09 |
| NTC | Vishay NTCS0603E3103JLT R25 10 kΩ ±5 %, **B25/85 3435 K ±1 %** (tabela da série, linha …3103*LT); divisor REFOUT → R36 → AIN9 → R37 22k → GND; referência interna tem de ficar habilitada; AIN9 vs AVSS, ref interna, ganho 1; −40 °C 0,20 V, +85 °C 2,35 V → RF3 ✔ (modelo β) | Vishay NTCS0603E3; netlist |

## Texto de resposta ao Rodrigo (pronto para enviar)

Olá, Rodrigo,

Muito obrigado, as respostas esclareceram bastante. Conferi tudo contra a placa e seguem os retornos.

**CONFIRMAÇÕES**
- O vetor de fábrica novo está correto: 0,44 V / 2,5 V × 2^24 = 2.952.790 contagens em 4 mA.
- O mapa invertido (AI1 = AIN4 … AI4 = AIN1) é o mesmo na V2.3; não muda nada no software.
- A calibração de 6 pontos por placa e por canal cobre o requisito de 0,2 % (cenário de 0,16 %).

**BUFFERS EM 0 V**
Concordo em desligar os buffers que ficam em 0 V. O AD7124 permite ligar cada buffer separadamente:
- Laços: AIN_BUFP = 1 e AIN_BUFM = 0. Sugiro usar AVSS (código 17) como negativo em vez de DGND (19); na placa os dois vão ao GND_ADC, mas o AVSS é a terra analógica.
- REFIN2 (laços, ADR4525): REF_BUFM = 0. O REF_BUFP pode ficar desligado, porque o ADR4525 tem impedância baixa.
- REFIN1 (célula): REF_BUFP = 1 é obrigatório. O REFIN1 vem de um divisor de 10k/10k (5 kΩ) e, sem buffer, a corrente de entrada de ±12 µA daria cerca de 60 mV de erro. REF_BUFM = 0.
- Com isso a célula fica ratiométrica: o REFIN1 vale metade da excitação, qualquer que seja o jumper do H1.

**LIMITE SUPERIOR**
Sugiro o critério NAMUR NE 43: abaixo de 3,6 mA e acima de 21,0 mA é falha; entre 20,5 e 21,0 mA, sobre-alcance. O ADC satura em 22,7 mA.

**SGOOD**
Não dá para levar ao Raspberry nesta placa: o SGOOD fica do lado de campo, o ISO7141 usa os 4 canais no SPI e os GPIO do AD7124 são só saídas. Por software dá para detectar: com transmissor em curto, a leitura fica no código máximo por uns 100 ms e depois perto de zero por 800 ms, em ciclo. Sugiro sinalizar "sobrecorrente" quando aparecer o código máximo.

**NTC**
O canal de NTC é requisito (RF3 do escopo), então entra na V2.3:
- NTC Vishay NTCS0603E3103JLT: 10 kΩ a 25 °C (±5 %), B25/85 = 3435 K (±1 %).
- O divisor é alimentado pelo REFOUT: REFOUT → NTC → AIN9, com 22 kΩ do AIN9 ao GND. Por isso a referência interna precisa continuar habilitada.
- Medição: AIN9 contra AVSS, referência interna de 2,5 V, ganho 1, AIN_BUFP = 1 e AIN_BUFM = 0. Fica ratiométrica.
- Fórmula: R_NTC = 22 kΩ × (1/razão − 1), com razão = V_AIN9 / 2,5 V; depois 1/T = 1/298,15 + ln(R_NTC/10 kΩ)/3435 (T em K).
- Faixa: cerca de 0,20 V a −40 °C e 2,35 V a +85 °C, dentro da faixa do ADC.

**SUGESTÕES (não urgentes)**
- Ativar alguma rejeição de 50/60 Hz, pensando nos cabos de 40 m em ambiente industrial.
- Usar o REF_DET na célula: sem jumper no H1 o REFIN1 cai abaixo de 0,7 V e isso é detectado.
- Ler o registrador de erros e, na célula, fazer a calibração interna de zero na inicialização.

**SOBRE OS 5 V NA V2.2**
Você tem razão em levantar isso. Na V2.2 o REFIN2 e a saída da referência interna ficavam ligados ao +5V_ADC por resistores de 0 Ω, acima do máximo absoluto de 3,6 V. Vamos considerar os AD7124 das placas V2.2 como suspeitos. Na V2.3 isso não existe mais.

Se quiser, marcamos a chamada para fechar os detalhes.

Abraço,
Javier
