# Motor de Risco (Risk Fusion Engine)

O `RiskFusionEngine` é o componente central responsável por consolidar evidências de várias fontes (Vídeo, Áudio, Documento).

## Pesos Padrão
- **Vídeo (Expressões, Violência)**: 40%
- **Áudio (Tensão vocal, Transcrição)**: 35%
- **Documento (Termo de consentimento, Risco Clínico)**: 25%

## Mecanismo de Tolerância a Falhas
Caso alguma análise falhe ou não tenha sido enviada (ex: uma consulta sem vídeo gravado), o motor normaliza os pesos matematicamente. Ex: Se só há áudio e documento, a base total de cálculo (100%) passa a ser 60%, de modo que o score global não seja prejudicado artificialmente.

## Classificação do Risco (IGA)
- **LOW** (Baixo): 0 a 39
- **MEDIUM** (Atenção): 40 a 69
- **HIGH** (Crítico): 70 a 100
