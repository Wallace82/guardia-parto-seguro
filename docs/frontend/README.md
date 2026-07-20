# Frontend (GuardIA Angular)

A interface de usuário do GuardIA Parto Seguro foi desenvolvida utilizando **Angular** (versões modernas com suporte a Standalone Components e Signals). Ela atua como o principal meio de visualização, telemetria clínica, e controle de monitoramento pelos profissionais de saúde.

## 1. Arquitetura do Frontend

O projeto adota uma arquitetura orientada a domínios (Domain-Driven Design / Feature Folders), organizada dentro de `src/app/domains/`. As principais características incluem:

- **Standalone Components**: Dispensa a necessidade de `NgModules` massivos. Cada componente gerencia suas próprias importações, facilitando testes isolados e "Lazy Loading" em rotas.
- **Signals**: O estado reativo da aplicação é preferencialmente gerenciado com `Signals` (e.g. `signal()`, `computed()`), garantindo detecção de mudanças granulares e excelente performance, em vez do clássico RxJS BehaviorSubjects (que é mantido apenas em integrações HTTP pesadas ou bibliotecas legadas).
- **Tailwind CSS**: A estilização global é construída de maneira utilitária utilizando Tailwind, permitindo a criação de *Design Systems* modulares de forma rápida, além de usar estilos puros (`.scss`/`.css`) encapsulados onde complexidade visual é exigida.

## 2. Estrutura de Domínios (`src/app/domains/`)

A interface foi estruturada em "Silos Funcionais":

### `auth`
- **Pages**: `login.component`
- **Responsabilidade**: Coletar credenciais, solicitar tokens ao `core-api` e armazenar o JWT no *Local Storage* de forma segura, garantindo rotas protegidas (via Guards).

### `dashboard`
- **Pages**: `dashboard-home.component`
- **Responsabilidade**: Visualização de métricas macros (total de sessões, níveis médios de risco, sumarizações).

### `sessoes`
- **Pages**: Criação de novas sessões, listagem (`session-list`), vinculação de pacientes.
- **Responsabilidade**: Manter o CRUD de sessões.

### `analise-ia` (Multimodal Analysis)
- **Pages**: `multimodal-analysis-page.component`
- **Responsabilidade**: O núcleo visual do GuardIA. Esta página consome dados de múltiplos serviços (via Orquestrador).
  - Exibe a *Timeline* de riscos daquele parto.
  - Exibe vídeos com os `bounding boxes` de detecções e emoções sobrepostas (processados via MediaPipe e YOLO/DeepFace).
  - Componente de Fatores de Risco (Recomendações da Inteligência Clínica em vermelho/laranja para perigo, azul para seguro - calculados em tempo real a partir do `iga_level`).
  
### `alertas`
- Notificações globais e *Toast messages* sobre avisos de risco alto ("Atenção na sessão X!").

### `relatorios` / `admin`
- Geração e exportação do arquivo final do parto (PDF), gestão de permissões dos médicos.

## 3. Gestão de Estado e Comunicação HTTP

- **Serviços HTTP (Services)**: Classes `@Injectable({providedIn: 'root'})` empacotam o `HttpClient` do Angular, realizando requisições HTTP RESTful para o `core-api` (na porta `:8000`).
- **Interceptors**: 
  - `AuthInterceptor`: Intercepta todas as requisições que saem e injeta automaticamente o cabeçalho `Authorization: Bearer <token>`.
  - Tratamento centralizado de erros HTTP (status 401 desloga automaticamente).

## 4. UI/UX e Componentes Compartilhados (`src/app/shared/`)

Temos uma forte ênfase visual no projeto (Design Premium e Microinterações). Componentes comuns, como modais (usando Angular Material `MatDialog`), ícones contextuais, botões e alertas ficam isolados em uma biblioteca compartilhada para reuso. Componentes modulares garantem que as lógicas e cores de risco (e.g. `iga_level == 'critico'` acendendo o card em vermelho) possam ser aplicadas de maneira uniforme em toda a plataforma.
