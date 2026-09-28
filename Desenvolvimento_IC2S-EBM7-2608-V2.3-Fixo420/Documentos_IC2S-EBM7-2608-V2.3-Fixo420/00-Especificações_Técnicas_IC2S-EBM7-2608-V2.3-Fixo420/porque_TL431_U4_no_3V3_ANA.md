# Porque existe o U4 (TL431B) no +3.3V_ANA

Pergunta da reunião de 25-09-2026: *«o SPX3819 já regula os 3,3 V; para que serve o TL431?»*

## Resposta curta

O U3 (SPX3819) **só consegue fornecer corrente, não a absorver**. O U4 existe para o caso contrário: quando entra
corrente **de fora** no +3.3V_ANA e empurra o rail para cima. Quem a mete lá são os díodos de protecção das entradas.
Sem o U4, essa corrente não tem para onde ir e o rail sobe até queimar o ADC. Em funcionamento normal o U4 está
desligado e não faz nada.

## O caminho da corrente, passo a passo

1. Cada entrada analógica do ADC tem um **BAV199** (D14, D15, D16, D17, D22, D24, D25): um díodo para o GND_ADC e outro para o **+3.3V_ANA**.
2. Se a tensão numa entrada passar de ~3,3 V + 0,6 V (surto no cabo, sensor ligado mal, 24 V no borne errado), o díodo
   de cima conduz e **despeja a corrente no +3.3V_ANA**. É exactamente para isso que ele lá está: proteger o pino do ADC,
   que aguenta no máximo **AVDD + 0,3 V** (AD7124-8 Rev. F, p.14, *Analog Input Voltage to AVSS*).
3. Essa corrente tem de sair do rail por algum lado. O SPX3819 é um LDO série: o transístor de saída liga a entrada à
   saída e só puxa corrente **da entrada para a saída**. Não há no datasheet (MaxLinear SPX3819 Rev. 2.0.5) nenhuma
   especificação de corrente absorvida na saída: ele simplesmente corta.
4. Sem o U4, a corrente só pode ir para o consumo das cargas (ADC, referência, alguns mA) e para os condensadores do
   rail, que carregam. Se o surto trouxer mais corrente do que as cargas gastam, **o rail sobe**. A revisão kicad-happy
   (folha 3, nota 14) estimou que chegava a ~10 V.
5. O AVDD do AD7124 tem **máximo absoluto de 3,96 V** (p.14, *AVDD to AVSS*). A 10 V o ADC morre, e com ele a
   referência U7 e o que mais estiver no rail.

O U4 fecha esse caminho: com o rail acima de ~3,6 V ele conduz e absorve a corrente para o GND_ADC, segurando o rail.

## Os números

O U4 é um regulador *shunt*: conduz quando a tensão no pino REF passa de V_ref. O divisor R6 4k42 / R7 10k faz o
limiar ser V_ref × (1 + 4,42/10) = V_ref × 1,442.

| Grandeza | Valor | Fonte |
|---|---|---|
| V_ref (TL431B) | 2,440 / 2,495 / 2,550 V (mín / típ / máx) | TI SLVS543S, p.6 |
| Limiar do clamp | **3,52 / 3,60 / 3,68 V** | 1,442 × V_ref |
| Com 100 mA a atravessar | +0,07 V (\|Z_KA\| ≤ 0,5 Ω × 1,442) → até ~3,75-3,79 V | SLVS543S p.6; folha 3, nota 14 |
| Saída do SPX3819 | 3,3 V ± 2 % em temperatura → **3,37 V no máximo** | SPX3819 p.2 |
| Folga entre os dois | 3,52 − 3,37 = **0,15 V**: em serviço o U4 nunca conduz | — |
| AVDD máx. absoluto do AD7124 | **3,96 V** | AD7124-8 p.14 |
| Folga do clamp ao máx. absoluto | 3,96 − 3,79 = 0,17 V no pior caso | — |
| Corrente que o U4 aguenta | 100 mA recomendado, 150 mA máx. absoluto | SLVS543S p.5 |
| Corrente residual estimada de um surto | 12-23 mA (corrida 4) | folha 3, nota 14 |
| Consumo permanente do divisor | 3,3 V / 14,42 kΩ = **0,23 mA** | — |
| Fuga do U4 desligado | ≤ 1 µA | SLVS543S p.6, I_off |

## Porque não outra peça

- **Zener de 3,6 V** (ZMM5227B, da mesma série do D4 já usado; Diodes DS30024 Rev. C-2, p.2): V_Z = **3,42-3,78 V a
  20 mA**, Z_ZT = 24 Ω a 20 mA e Z_ZK = **1700 Ω a 0,25 mA**. Dois problemas:
  - joelho mole: com 1700 Ω perto do joelho, o zener já conduz a 3,3-3,37 V e carrega o LDO permanentemente. A fuga
    só está especificada a 1 V (≤ 15 µA), não a 3,3 V;
  - clamp alto: a 100 mA fica em ~3,78 + 0,08 A × 24 Ω ≈ **5,7 V**, bem acima dos 3,96 V do ADC.
  O TL431B tem joelho abrupto (≤ 1 µA desligado), Z_KA ≤ 0,5 Ω e 0,5 % de tolerância.
- **TVS de 3,3 V**: o mesmo problema, maior. Os TVS de baixa tensão têm fuga alta e clamp muito acima do standoff.
- **Não pôr nada e confiar no LDO**: é o caso descrito acima. O LDO não absorve corrente.
- **Custo**: o TL431BQDBZR custa ~0,44 USD à unidade (Mouser, BOM da EBM2 de 25-09) e o divisor são duas
  resistências 0603.

## Resumo para o revisor

| | Sem o U4 | Com o U4 |
|---|---|---|
| Serviço normal | 3,3 V | 3,3 V (o U4 está desligado; gasta 0,23 mA no divisor) |
| Surto numa entrada | o BAV199 despeja no rail, o LDO não absorve, o rail sobe (~10 V) e o ADC morre | o U4 absorve até 100 mA e o rail fica ≤ 3,79 V, abaixo dos 3,96 V do ADC |

O mesmo raciocínio está resumido na **folha 3, nota 14** do esquemático. A EBM2 V5 tem o mesmo circuito (U3, folha 3,
nota 7), com o limiar a 3,52 V.
