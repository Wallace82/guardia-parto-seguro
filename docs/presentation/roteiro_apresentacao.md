# Roteiro de Vídeo: GuardIA Parto Seguro

> [!TIP]
> **Dicas para Gravação:** 
> - Este roteiro foi pensado para durar cerca de **12 a 15 minutos**, mantendo um ritmo tranquilo. 
> - Grave sua tela dividindo-a entre os slides da apresentação (se houver) e o sistema rodando. 
> - Certifique-se de ter um vídeo e áudio de teste (simulando um parto com alguma anomalia leve) engatilhados no seu computador para o upload.

---

## 🎬 Estrutura do Vídeo

| Bloco | Duração Estimada | Foco |
| :--- | :--- | :--- |
| **1. Introdução** | 2 minutos | Apresentação do problema, do projeto e do IGA. |
| **2. Visão de Arquitetura** | 2 minutos | Como os microsserviços e a AWS interagem. |
| **3. Mão na Massa (Upload)** | 2 minutos | Inserindo os arquivos no sistema (Áudio, Vídeo, Documentos). |
| **4. Processamento (O Motor)** | 5 minutos | Detalhando o que a IA está analisando por trás dos panos e a integração com a AWS. |
| **5. O Alerta (Fluxo Final)** | 3 minutos | IGA calculando, tela vermelha, notificação médica. |
| **6. Conclusão** | 1 minuto | Impacto e encerramento. |

---

## 📝 Roteiro Detalhado (Fala e Tela)

### 1. Introdução (0:00 - 2:00)

*   **Na Tela:** Slide inicial com o nome do projeto "GuardIA Parto Seguro" e seu nome/equipe.
*   **Sua Fala (Sugestão):** 
    > "Olá, sejam bem-vindos à apresentação do **GuardIA Parto Seguro**. Nosso projeto ataca um problema gravíssimo e muitas vezes invisível: a violência obstétrica e a negligência em salas de parto. 
    > Para erradicar isso, nós criamos uma plataforma de **telemetria clínica e análise multimodal**. Em termos simples, o sistema observa, escuta e lê o que está acontecendo durante o procedimento e gera um índice dinâmico, que chamamos de **IGA - Índice GuardIA de Atenção**."

### 2. Visão de Arquitetura (2:00 - 4:00)

*   **Na Tela:** Slide ou diagrama da Arquitetura (Frontend Angular -> Backend FastAPI -> Serviços de IA e AWS).
*   **Sua Fala:** 
    > "Nossa arquitetura foi construída orientada a microsserviços. Temos um Frontend rico em Angular, e um orquestrador em Python/FastAPI. Mas o verdadeiro coração do sistema são nossos *Workers* de Inteligência Artificial.
    > Eles operam de forma isolada para processar vídeo, áudio e documentos. Para elevar o nível do projeto e garantir robustez, integramos fortemente os serviços da **AWS** *(Nota: cite os serviços específicos da AWS que você usou, como AWS Textract para documentos ou AWS Transcribe para áudio)*."

### 3. Mão na Massa - Ingestão (4:00 - 6:00)

*   **Na Tela:** Sistema aberto no navegador (Dashboard do Frontend). Mostre a tela de criação de uma sessão ou paciente.
*   **Sua Fala:** 
    > "Vamos para a prática. Aqui temos o painel da UTI ou da sala de cirurgia. Vou simular o início de um monitoramento.
    > Para essa demonstração de **processamento multimodal**, vou enviar arquivos que representam o ambiente da paciente: um trecho de **vídeo** (monitorando o rosto/expressões), um **áudio** captado do ambiente, e um **prontuário médico** (ex: atestando hipertensão)."
*   **Ação:** Faça o upload dos arquivos no sistema e clique para iniciar a análise.

### 4. Processamento Multimodal e AWS (6:00 - 11:00)

*   **Na Tela:** Tela de "Processando" ou Logs do sistema (mostrando os serviços trabalhando simultaneamente).
*   **Sua Fala:** 
    > "Enquanto o sistema processa, vou explicar o que está acontecendo em paralelo nos nossos microsserviços:
    > 
    > **1. Análise de Vídeo:** Nossos modelos baseados em OpenCV e YOLO estão analisando frame a frame buscando tensão facial, dor ou retenção de instrumentos.
    > 
    > **2. Análise de Áudio (Reconhecimento de Voz):** Nosso áudio é processado usando a biblioteca **SpeechRecognition** conectada à API do **Google** para realizar a transcrição local rápida (Speech-to-Text). Esse texto transcrito é imediatamente enviado para a OpenAI identificar desespero, gritos ou respostas bruscas da equipe médica.
    > 
    > **3. Análise de Documentos (O Pipeline Híbrido):** O prontuário e as anotações que subimos passam por uma via expressa de inteligência. Primeiro, lemos o PDF com **AWS Textract**. Depois, enviamos esse texto para o **AWS Comprehend Medical**, que extrai de forma exata todas as doenças, medicamentos e alertas factuais. Só então, com esses fatos na mão, nós acionamos a **OpenAI** para concluir o diagnóstico de risco sem perigo de alucinação (invenção de dados)."

### 5. Anomalias e o Fluxo do Alerta Final (11:00 - 14:00)

*   **Na Tela:** Retorne ao Dashboard. A tela deve mostrar os resultados parciais chegando e, de repente, o "IGA" subindo de nível e ficando **Vermelho (CRÍTICO)**.
*   **Sua Fala:** 
    > "Aqui vemos o resultado da fusão de dados. Notem que o nosso sistema de risco percebeu uma anomalia!
    > O áudio acusou que a paciente relatou uma dor intensa que não foi acolhida, ou a análise textual identificou vulnerabilidade severa. 
    > Para evitar que uma média matemática simples esconda esse perigo, nosso algoritmo entra em ação com uma **Regra de Agravamento Contextual**: se qualquer um dos domínios isoladamente atingir um alerta extremo (score acima de 75%), o peso daquele fator é ampliado drasticamente, impedindo a diluição do risco.
    > Imediatamente, o motor calcula essas penalidades e o nosso **IGA (Índice GuardIA de Atenção)** dá um salto e ultrapassa a barreira dos 70%. 
    > 
    > Como resultado final, vemos este **Alerta Visual e Sonoro Crítico**. No mundo real, isso pisca na central de enfermagem e manda um alerta para o plantonista sênior, garantindo uma intervenção rápida para proteger a gestante de negligência."

### 6. Conclusão (14:00 - 15:00)

*   **Na Tela:** Câmera de volta para você ou um slide de encerramento com agradecimentos.
*   **Sua Fala:** 
    > "O GuardIA Parto Seguro não substitui a equipe, ele é uma camada invisível de proteção. Combinando análise de imagem local, áudio e documentos processados na nuvem da AWS, juntamente com regras estritas de negócios, provamos ser possível auditar e garantir um parto humanizado e seguro usando a tecnologia.
    > 
    > O vídeo, áudio e todos os registros dessa demonstração serão posteriormente anonimizados, respeitando a privacidade dos dados.
    > Muito obrigado pela atenção."
