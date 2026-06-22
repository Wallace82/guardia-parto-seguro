# SECURITY.md — GuardIA Parto Seguro

> Políticas de Segurança, Privacidade e Conformidade LGPD — v2.0

---

## 1. Visão Geral de Segurança

O **GuardIA Parto Seguro** lida com dados médicos extremamente sensíveis (vídeos de partos, áudios de consultas, prontuários). A arquitetura foi projetada sob o princípio de **Security by Design** e **Zero Trust**, operando em forte conformidade com a Lei Geral de Proteção de Dados (LGPD).

O domínio central responsável por orquestrar essas regras é o **Security Domain**, enquanto o **AWS Integration Domain** atua como proxy seguro para serviços externos.

---

## 2. Classificação de Dados e Privacidade

De acordo com a LGPD, os dados processados pelo GuardIA enquadram-se na categoria de **Dados Pessoais Sensíveis**.

### 2.1 Módulo de Anonimização (Pseudo-anonimização)
Para reduzir a superfície de risco e limitar o acesso aos dados reais, o sistema aplica um algoritmo de pseudo-anonimização em tempo real:
- **Identificadores Diretos (Nomes, CPFs):** São substituídos por um código opaco assim que entram no sistema (Ex: "Maria da Silva" → `PACIENTE_001`).
- **Mapeamento Criptografado:** A tabela de equivalência (De/Para) fica armazenada no `Security DB`, criptografada por uma chave mestre residente no AWS Secrets Manager.
- **Processamento na Nuvem:** Quando um áudio ou documento é enviado aos serviços da AWS (Transcribe, Comprehend, Textract), ele não leva o nome da paciente, apenas o ID opaco.

---

## 3. Criptografia

### 3.1 Em Trânsito (Data in Transit)
- **TLS 1.3 Obrigatório:** Toda comunicação entre os nós da rede (APIs, Banco de Dados, AWS Services, Dashboard) ocorre exclusivamente sobre HTTPS/TLS 1.3.
- Redirecionamento HTTP para HTTPS é compulsório em todos os endpoints públicos.

### 3.2 Em Repouso (Data at Rest)
- **Bancos de Dados:** Todos os bancos de dados PostgreSQL (incluindo backups) utilizam encriptação transparente no nível do disco (Amazon RDS Encryption) ou extensão `pgcrypto` para colunas sensíveis.
- **Armazenamento de Mídias (Amazon S3):** O Amazon S3 está configurado com criptografia em repouso ativada (S3 Encryption) utilizando **AES-256**.
- As chaves de criptografia são rotacionadas periodicamente através do AWS KMS.

---

## 4. Gestão de Segredos e Credenciais

> **NUNCA commite senhas, tokens ou connection strings no repositório.**

A gestão de credenciais é delegada ao **AWS Secrets Manager**:
- **Acesso Dinâmico:** Os serviços da plataforma recuperam dinamicamente strings de conexão, tokens e chaves de API durante o bootstrap ou em tempo de execução via *AWS IAM Roles*.
- **Sem chaves estáticas:** Chaves estáticas em arquivos `.env` são permitidas **apenas** no ambiente de desenvolvimento local (LOCAL/DEV). Nos ambientes de nuvem (HML/PRD), usa-se IAM Policies.
- **Auditoria de Acesso a Segredos:** O AWS CloudTrail / CloudWatch emite logs toda vez que uma chave é lida.

---

## 5. Controle de Acesso (IAM e RBAC)

O sistema utiliza JSON Web Tokens (JWT) com verificação assimétrica para garantir autorização rigorosa no lado da aplicação, aliados ao controle de políticas do AWS IAM para os recursos de nuvem.

**Perfis de Acesso:**
1. **Admin:** Acesso técnico total. Gerencia integrações e usuários, mas **não** pode visualizar vídeos, áudios ou prontuários desanonimizados sem um token de consentimento de auditoria.
2. **Médico / Enfermeiro:** Pode criar sessões, fazer uploads e visualizar métricas (IRA) **apenas** dos pacientes vinculados a eles ou de sua unidade (com consentimento do paciente).
3. **Gestor Hospitalar:** Pode visualizar dashboards agregados e o mapa de calor de risco institucional, mas acessa detalhes sensíveis anonimizados.
4. **Auditor / Ouvidor:** Acessa logs do `Security Domain` e relatórios de auditoria imutáveis (com hash SHA-256) em caso de denúncia de violência obstétrica.

---

## 6. Audit Logger (Trilha de Auditoria)

Para fins de LGPD e segurança médica, a rastreabilidade é total. O `Security Domain` (através do `core-api`) mantém um **Audit Log** imutável no banco de dados, registrando todas as ações de leitura e escrita, e envia esses logs para o **Amazon CloudWatch Logs**.

**O que é registrado:**
- Autenticações (Sucesso/Falha).
- Acessos de leitura a sessões (Quem visualizou o vídeo e quando).
- Disparos de Alertas e Reconhecimentos (Quem ignorou um alerta crítico e a justificativa).
- Uploads e modificações de estado do IRA.

**Formato do Log (JSON Estruturado no CloudWatch):**
```json
{
  "timestamp": "2024-10-15T14:32:01Z",
  "actor_id": "uuid-medico-01",
  "role": "medico",
  "action": "READ_SESSION",
  "resource_type": "video_analysis",
  "resource_id": "uuid-sessao-02",
  "ip_address": "192.168.1.50"
}
```

---

## 7. Retenção e Descarte (Direito ao Esquecimento)

A plataforma implementa mecanismos de deleção lógica e expurgo:
- **Vídeos e Áudios:** Retidos pelo período legal exigido (padrão: 5 anos de inatividade, mas configurável conforme o Conselho Federal de Medicina).
- Após o período, o processo de "Shredding" digital destrói o dado no Amazon S3 e exclui a chave do paciente no banco, impossibilitando a reversão da pseudo-anonimização.
