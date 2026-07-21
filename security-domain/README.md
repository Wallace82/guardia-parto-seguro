# Security Domain

## Descrição
Este microsserviço Gerencia chaves KMS (Mocks) e chaves assimétricas.

## Arquitetura
- Backend: FastAPI (Python 3.12+)
- Porta: Definida pelo \docker-compose.yml\ (8001-8007)
- Integração: Via chamadas HTTP orquestradas pelo \core-api\.
- Armazenamento: Lê e escreve bins físicos no Docker Volume Compartilhado \/shared_media\.

## Fluxo (Flow)
1. Recebe payload via \/analyze\.
2. O \processor.py\ resolve o \lob_url\ mapeado fisicamente no Windows ou Linux.
3. Executa a inferência.
4. O ORM salva os resultados parciais em um dicionário em memória (Mock DB) ou repassa diretamente.

## Roadmaps e Limitações
- Ver [Roadmap Geral](../docs/roadmap/ROADMAP.md) e [Débitos Técnicos](../docs/decisions/TECHNICAL_DEBT.md) para limitações como fallbacks e algoritmos faltantes (ex: YOLO).
