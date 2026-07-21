# Arquitetura de Scores (Hierarquia de Evidências)

O GuardIA utiliza um modelo de risco baseado em evidências hierárquicas. Em vez de atribuir scores puramente matemáticos à sessão, o sistema consolida resultados obtidos independentemente de três modalidades (Vídeo, Áudio e Documento).

## Fluxo da Arquitetura
1. **Coleta**: Mídias são enviadas para a sessão.
2. **Análise Granular**: Microserviços analisam a mídia e criam os registros granulares (`VideoAnalysis`, `AudioAnalysis`, `DocumentAnalysis`) no banco de dados, preenchendo as emoções, transcrições e scores específicos daquela fonte.
3. **Consolidação**: Ao consultar a sessão, a `RiskFusionEngine` lê as três fontes.
4. **Histórico**: Modificações de risco geram um log imutável na tabela `RiskHistory` permitindo auditoria ao longo do tempo.
