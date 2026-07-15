# DESIGN_SYSTEM.md — GuardIA Parto Seguro

> Design System Angular Material + TailwindCSS
> Inspirado na identidade visual Streamlit atual (fundo escuro, violeta/rosa)

---

## 1. Filosofia Visual

A identidade do GuardIA é **dark mode por padrão**, transmitindo:
- Confiança e segurança (azul/violeta profundo)
- Urgência e atenção (vermelho e âmbar)
- Saúde e sucesso (verde esmeralda)
- Tecnologia clínica (glassmorphism, gradientes)

---

## 2. Paleta de Cores

### Cores Primárias
```scss
// src/styles.scss — CSS Custom Properties
:root {
  // Primária — Violeta (identidade GuardIA)
  --color-primary-50:  #f5f3ff;
  --color-primary-100: #ede9fe;
  --color-primary-500: #8B5CF6;  // Violeta vibrante — cor primária
  --color-primary-600: #7C3AED;
  --color-primary-700: #6D28D9;

  // Secundária — Rosa/Fúcsia
  --color-secondary-500: #EC4899;
  --color-secondary-600: #DB2777;

  // Sucesso — Verde Esmeralda
  --color-success-500: #10B981;
  --color-success-600: #059669;

  // Atenção — Âmbar
  --color-warning-500: #F59E0B;
  --color-warning-600: #D97706;

  // Risco/Perigo — Vermelho
  --color-danger-500: #EF4444;
  --color-danger-600: #DC2626;

  // Superfícies (dark mode)
  --color-bg:           #0B0F19;  // Fundo principal — azul escuro profundo
  --color-surface:      #1E293B;  // Card/panel background
  --color-surface-2:    #334155;  // Hover/elevated surface
  --color-border:       rgba(255, 255, 255, 0.08);

  // Texto
  --color-text:         #FFFFFF;
  --color-text-muted:   #94A3B8;
  --color-text-subtle:  #64748B;
}
```

### Mapeamento IGA → Cor
```scss
// IGA Risk Level Colors
--ira-baixo:    #10B981;  // Verde
--ira-moderado: #F59E0B;  // Âmbar
--ira-critico:  #EF4444;  // Vermelho
```

---

## 3. Tipografia

```scss
// Fonte principal: Outfit (Google Fonts)
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
  --font-family: 'Outfit', 'Inter', system-ui, sans-serif;

  --font-size-xs:   0.75rem;   // 12px
  --font-size-sm:   0.875rem;  // 14px
  --font-size-base: 1rem;      // 16px
  --font-size-lg:   1.125rem;  // 18px
  --font-size-xl:   1.25rem;   // 20px
  --font-size-2xl:  1.5rem;    // 24px
  --font-size-3xl:  1.875rem;  // 30px
  --font-size-4xl:  2.25rem;   // 36px
}
```

---

## 4. Espaçamento e Bordas

```scss
:root {
  --radius-sm:  0.375rem;  // 6px
  --radius-md:  0.5rem;    // 8px
  --radius-lg:  0.75rem;   // 12px
  --radius-xl:  1rem;      // 16px
  --radius-2xl: 1.5rem;    // 24px

  --shadow-glow-primary: 0 0 20px rgba(139, 92, 246, 0.3);
  --shadow-glow-danger:  0 0 20px rgba(239, 68, 68, 0.3);
  --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.4);
}
```

---

## 5. Componentes do Design System

### 5.1 RiskCard — Exibe score de risco por componente

```html
<!-- Uso: <app-risk-card [component]="'video'" [score]="72.5" /> -->
```

```typescript
@Component({
  selector: 'app-risk-card',
  standalone: true,
  template: `
    <div class="risk-card" [class]="levelClass()">
      <div class="risk-card__icon">{{ icon() }}</div>
      <div class="risk-card__content">
        <span class="risk-card__label">{{ label() }}</span>
        <span class="risk-card__score">{{ score() | number:'1.1-1' }}</span>
        <span class="risk-card__level">{{ level() }}</span>
      </div>
      <app-confidence-meter [value]="score()" [max]="100" />
    </div>
  `,
})
export class RiskCardComponent {
  component = input.required<'video' | 'audio' | 'document'>();
  score = input.required<number>();
  // ...
}
```

### 5.2 IraGauge — Medidor circular do IGA

```typescript
@Component({
  selector: 'app-ira-gauge',
  standalone: true,
  template: `
    <div class="ira-gauge" [style.--ira-color]="color()">
      <svg viewBox="0 0 200 200">
        <!-- Arc de fundo -->
        <circle cx="100" cy="100" r="80" fill="none" stroke="var(--color-surface-2)" stroke-width="12" />
        <!-- Arc de progresso -->
        <circle cx="100" cy="100" r="80" fill="none"
          [attr.stroke]="color()"
          stroke-width="12"
          stroke-linecap="round"
          [attr.stroke-dasharray]="circumference()"
          [attr.stroke-dashoffset]="dashOffset()" />
      </svg>
      <div class="ira-gauge__value">
        <span class="score">{{ score() | number:'1.1-1' }}</span>
        <span class="label">IGA</span>
        <span class="level" [style.color]="color()">{{ level() | uppercase }}</span>
      </div>
    </div>
  `,
})
export class IraGaugeComponent {
  score = input.required<number | null>();
  // ...
}
```

### 5.3 ConfidenceMeter — Barra de confiança/progresso

```typescript
@Component({
  selector: 'app-confidence-meter',
  standalone: true,
  template: `
    <div class="confidence-meter">
      <div class="confidence-meter__track">
        <div class="confidence-meter__fill"
          [style.width.%]="percentage()"
          [style.background]="color()">
        </div>
      </div>
      <span class="confidence-meter__label">{{ percentage() | number:'1.0-0' }}%</span>
    </div>
  `,
})
export class ConfidenceMeterComponent {
  value = input.required<number>();
  max = input<number>(100);
  // ...
}
```

### 5.4 AITimeline — Timeline de eventos de análise

```typescript
@Component({
  selector: 'app-ai-timeline',
  standalone: true,
  template: `
    <div class="ai-timeline">
      @for (finding of findings(); track finding.timestamp_seconds) {
        <div class="timeline-event" [class.high-risk]="finding.confidence > 0.8">
          <div class="timeline-dot" [style.background]="getSeverityColor(finding.confidence)"></div>
          <div class="timeline-content">
            <span class="time">{{ formatTimestamp(finding.timestamp_seconds) }}</span>
            <p class="description">{{ finding.description }}</p>
            <app-confidence-meter [value]="finding.confidence * 100" />
          </div>
        </div>
      }
    </div>
  `,
})
export class AITimelineComponent {
  findings = input.required<VideoFinding[]>();
}
```

### 5.5 AlertBadge — Badge de severidade de alerta

```typescript
@Component({
  selector: 'app-alert-badge',
  standalone: true,
  template: `
    <span class="alert-badge" [class]="'alert-badge--' + severity()">
      {{ severity() === 'critical' ? '🔴 CRÍTICO' : '🟡 MODERADO' }}
    </span>
  `,
})
export class AlertBadgeComponent {
  severity = input.required<'moderate' | 'critical'>();
}
```

### 5.6 StatusChip — Status da sessão/mídia

```typescript
@Component({
  selector: 'app-status-chip',
  standalone: true,
  template: `
    <span class="status-chip" [class]="'status-chip--' + status()">
      <span class="status-chip__dot"></span>
      {{ statusLabel() }}
    </span>
  `,
})
export class StatusChipComponent {
  status = input.required<SessionStatus | MediaStatus>();
}
```

### 5.7 MediaUploader — Upload com drag & drop

```typescript
@Component({
  selector: 'app-media-uploader',
  standalone: true,
  template: `
    <div class="media-uploader"
      [class.dragging]="isDragging()"
      (dragover)="onDragOver($event)"
      (drop)="onDrop($event)">
      <input type="file" #fileInput [accept]="acceptTypes()" (change)="onFileSelect($event)" hidden />
      <div class="uploader-content" (click)="fileInput.click()">
        <mat-icon>cloud_upload</mat-icon>
        <p>Arraste ou clique para selecionar</p>
        <p class="hint">{{ hintText() }}</p>
      </div>
      @if (selectedFile()) {
        <div class="file-preview">
          <mat-icon>{{ fileIcon() }}</mat-icon>
          <span>{{ selectedFile()!.name }}</span>
          <span>{{ selectedFile()!.size | mediaSize }}</span>
        </div>
      }
    </div>
  `,
})
export class MediaUploaderComponent {
  mediaType = input.required<MediaType>();
  // ...
}
```

---

## 6. Tokens CSS TailwindCSS (tailwind.config.ts)

```typescript
// tailwind.config.ts
export default {
  content: ['./src/**/*.{html,ts}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#f5f3ff',
          500: '#8B5CF6',
          600: '#7C3AED',
          700: '#6D28D9',
        },
        secondary: {
          500: '#EC4899',
        },
        bg: '#0B0F19',
        surface: '#1E293B',
        'surface-2': '#334155',
        success: '#10B981',
        warning: '#F59E0B',
        danger:  '#EF4444',
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-primary': '0 0 20px rgba(139, 92, 246, 0.3)',
        'glow-danger':  '0 0 20px rgba(239, 68, 68, 0.3)',
        'card': '0 4px 24px rgba(0, 0, 0, 0.4)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
    },
  },
  darkMode: 'class',
};
```

---

## 7. Angular Material Theme

```scss
// src/styles.scss
@use '@angular/material' as mat;

$guardia-primary: mat.define-palette((
  50:  #f5f3ff,
  100: #ede9fe,
  200: #ddd6fe,
  500: #8B5CF6,
  600: #7C3AED,
  700: #6D28D9,
  contrast: (500: white, 600: white, 700: white)
), 500, 600, 700);

$guardia-accent: mat.define-palette((
  500: #EC4899,
  contrast: (500: white)
), 500);

$guardia-warn: mat.define-palette((
  500: #EF4444,
  contrast: (500: white)
), 500);

$guardia-theme: mat.define-dark-theme((
  color: (
    primary: $guardia-primary,
    accent:  $guardia-accent,
    warn:    $guardia-warn,
  ),
  typography: mat.define-typography-config(
    $font-family: 'Outfit, Inter, sans-serif',
  ),
));

@include mat.all-component-themes($guardia-theme);
```

---

## 8. Micro-animações e Efeitos

```scss
// Glassmorphism card
.glass-card {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  }
}

// Fade in animation
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.fade-in { animation: fadeIn 0.3s ease-out; }

// Pulsing indicator para status de processamento
@keyframes processingPulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}

.processing-indicator {
  animation: processingPulse 2s ease-in-out infinite;
}

// Glow para alertas críticos
.critical-glow {
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.4);
  border-color: rgba(239, 68, 68, 0.5);
}
```

---

## 9. Iconografia

- **Ícones principais**: Angular Material Icons (mat-icon)
- **Ícones de domínio**:
  - Vídeo: `videocam`
  - Áudio: `mic`
  - Documento: `description`
  - Risco: `warning_amber`
  - Alerta: `notification_important`
  - Análise IA: `psychology`
  - Sessão: `medical_services`
  - Dashboard: `dashboard`
  - Relatório: `summarize`
  - Auditoria: `policy`
  - Usuário: `person`
  - Admin: `admin_panel_settings`

---

## 10. Tela Principal — Centro de Controle

> Wireframe de referência para o dashboard principal do sistema.
> Tela exibida após login, quando o profissional seleciona um atendimento ativo.

---

### 10.1 Layout Geral

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [SIDEBAR]  │                    [TOP BAR]                                 │
│            │  🔔  👤 Enf. João Silva — Enfermeiro                         │
│  GuardIA   ├──────────────────────────────────────────────────────────────│
│  --------  │                                                              │
│  ● Início  │  Centro de Controle                                          │
│  Pacientes │  Monitoramento em tempo real com IA                          │
│  Atendim.  │                                                              │
│  Análise IA│  ┌──────────────────────────────────────────────────────┐    │
│  Vídeos    │  │ [BARRA DE PACIENTE]                                  │    │
│  Áudios    │  │ 📷 Maria Silva de Oliveira                           │    │
│  Relatórios│  │ 30 anos • G1P0 • 39s2d   Sala 03  Leito 05          │    │
│  Alertas   │  │ Início TP: 10:02 (há 04h32)     ✅ Status IA: Baixo │    │
│  Auditoria │  └──────────────────────────────────────────────────────┘    │
│  Configur. │                                                              │
│            │  [INDICADORES EM TEMPO REAL — 4 gauge cards]                 │
│            │                                                              │
│            │  [TIMELINE DA ANÁLISE]         [RESUMO DA IA]               │
│            │                                                              │
│            │  [AÇÕES RÁPIDAS — 5 botões]                                 │
│            │                                                              │
│  Sair      │  [FOOTER]                                                    │
└────────────────────────────────────────────────────────────────────────────┘
```

---

### 10.2 Sidebar — Menu Lateral

- **Posição**: Fixa à esquerda, largura `240px` (colapsável para `72px` em mobile)
- **Fundo**: `--color-bg` (`#0B0F19`) com borda direita sutil `--color-border`
- **Logo**: "GuardIA — Parto Seguro" no topo, com ícone de escudo + coração
- **Itens do menu** (ícone + label):

| Ícone                    | Label          | Rota               |
|--------------------------|----------------|--------------------|
| `home`                   | Início         | `/dashboard`       |
| `people`                 | Pacientes      | `/pacientes`       |
| `medical_services`       | Atendimentos   | `/atendimentos`    |
| `psychology`             | Análise IA     | `/analise-ia`      |
| `videocam`               | Vídeos         | `/videos`          |
| `mic`                    | Áudios         | `/audios`          |
| `summarize`              | Relatórios     | `/relatorios`      |
| `notification_important` | Alertas        | `/alertas`         |
| `policy`                 | Auditoria      | `/auditoria`       |
| `settings`               | Configurações  | `/configuracoes`   |

- **Item ativo**: Fundo `--color-primary-500` com opacidade 20%, texto branco, border-radius `--radius-md`, barra lateral de 3px `--color-primary-500` à esquerda
- **Hover**: Background `--color-surface` com transição `0.2s ease`
- **Sair**: Fixo na parte inferior, separado por `border-top` sutil

---

### 10.3 Top Bar — Barra Superior

- **Altura**: `64px`
- **Fundo**: `--color-surface` com `backdrop-filter: blur(12px)`
- **Layout**: `display: flex; justify-content: flex-end; align-items: center`
- **Conteúdo** (alinhado à direita):
  - 🔔 Ícone `notifications` — badge vermelho com contador de alertas não lidos
  - 👤 Avatar circular (`40px`) + nome do profissional + cargo em `--color-text-muted`

---

### 10.4 Barra de Paciente — Patient Info Bar

> Card horizontal destacado no topo do conteúdo com os dados do atendimento ativo.

- **Container**: `glass-card` com padding `24px`, `display: flex`, `gap: 24px`, `align-items: center`
- **Altura**: Autocontida (~100px)
- **Elementos**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [Avatar]   Nome Completo da Paciente               Sala  Leito       │
│  (80px)     30 anos • G1P0 • 39s2d                  03    05          │
│                                                                        │
│             Início do trabalho de parto: 10:02       Status IA         │
│             há 04h32                                 ✅ Baixo risco    │
└─────────────────────────────────────────────────────────────────────────┘
```

| Elemento              | Estilo                                                       |
|-----------------------|--------------------------------------------------------------|
| Avatar                | Circular `80px`, borda `3px solid --color-primary-500`, `object-fit: cover` |
| Nome                  | `--font-size-xl`, `font-weight: 600`, cor `--color-text`     |
| Detalhes clínicos     | `--font-size-sm`, cor `--color-text-muted` (idade • paridade • IG) |
| Sala / Leito          | Duas colunas com label `--font-size-xs` em `--color-text-subtle` e valor `--font-size-2xl` `font-weight: 700` |
| Início TP             | Label + hora em `--font-size-lg`, tempo decorrido em `--color-text-muted` |
| Status IA             | Chip com ícone `check_circle`, background semitransparente baseado no nível IGA, border-radius `--radius-2xl` |

---

### 10.5 Indicadores em Tempo Real — Gauge Cards (4 colunas)

> Seção "Indicadores em tempo real" — 4 cards com gauge circular, cada um representando uma dimensão da análise.

- **Título da seção**: "Indicadores em tempo real" — `--font-size-xl`, `font-weight: 600`
- **Layout**: `display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px`
- **Responsivo**: `repeat(2, 1fr)` em tablets, `1fr` em mobile

#### Cada card:

```
┌──────────────────────┐
│  🟢 Estado emocional │
│      Confiança       │
│                      │
│      ┌──────┐        │
│      │ 82%  │        │  ← Gauge circular (SVG arc)
│      └──────┘        │
│                      │
│      Alto            │  ← Nível (cor dinâmica)
│  Estável nas         │
│  últimas 2h          │  ← Subtexto descritivo
└──────────────────────┘
```

| Card | Ícone | Título               | Subtítulo          | Exemplo | Nível     | Descrição                |
|------|-------|----------------------|--------------------|---------|-----------|--------------------------|
| 1    | 🧠    | Estado emocional     | Confiança          | 82%     | Alto      | Estável nas últimas 2h   |
| 2    | 💬    | Comunicação          | Humanizada         | 90%     | Excelente | Interações positivas     |
| 3    | 🤸    | Linguagem corporal   | Postura positiva   | 70%     | Bom       | Postura relaxada         |
| 4    | 🎙️    | Análise vocal        | Nível de ansiedade | 25%     | Baixo     | Voz calma e estável      |

**Estilo do card**:
- Fundo: `glass-card` (glassmorphism)
- Ícone do domínio: badge circular colorido no canto superior esquerdo (`32px`)
- **Gauge circular**: Reutiliza `IraGaugeComponent` com cores dinâmicas:
  - `0–39%` → `--ira-baixo` (verde) — se o indicador medir risco
  - `40–69%` → `--ira-moderado` (âmbar)
  - `70–100%` → `--ira-critico` (vermelho) — ou verde para métricas positivas
  - **Para métricas positivas** (emocional, comunicação, corporal): escala invertida (alto = verde)
  - **Para métricas de risco** (ansiedade): escala normal (baixo = verde)
- Texto do nível: `font-weight: 700`, cor alinhada ao gauge
- Descrição: `--font-size-xs`, cor `--color-text-subtle`

---

### 10.6 Timeline da Análise + Resumo da IA (Split Layout)

> Seção dividida em duas colunas: timeline à esquerda (60%) e resumo da IA à direita (40%).

- **Layout**: `display: grid; grid-template-columns: 3fr 2fr; gap: 24px`
- **Responsivo**: Empilha em `1fr` no mobile

#### 10.6.1 Timeline da Análise (coluna esquerda)

- **Título**: "Timeline da análise" — `--font-size-xl`, `font-weight: 600`
- **Container**: `glass-card`
- **Componente**: Evolução do `AITimelineComponent`

```
┌─────────────────────────────────────────────────────────────────┐
│  Timeline da análise                                            │
│                                                                 │
│  ● 10:32  Paciente relatou contrações mais intensas    [chip]   │
│  │                                          Condição estável    │
│  ● 10:34  Enfermeira orientou técnicas de respiração   [chip]   │
│  │                                       Interação positiva     │
│  ● 10:36  Médico explicou evolução do TP               [chip]   │
│  │                                       Comunicação clara      │
│  ● 10:38  Paciente demonstra confiança                 [chip]   │
│                                           Emoção positiva       │
│                                                                 │
│  Ver linha do tempo completa →                                  │
└─────────────────────────────────────────────────────────────────┘
```

| Elemento              | Estilo                                                        |
|-----------------------|---------------------------------------------------------------|
| Linha vertical        | `2px solid --color-border`, conectando os dots                |
| Dot                   | Circular `12px`, cor baseada no tipo (verde = positivo, âmbar = atenção, vermelho = crítico) |
| Timestamp             | `--font-size-sm`, `font-weight: 600`, cor `--color-text-muted` |
| Descrição do evento   | `--font-size-sm`, cor `--color-text`                          |
| Chip de classificação | Fundo semitransparente, border-radius `--radius-2xl`, `--font-size-xs`, cores: verde (positivo), âmbar (neutro), vermelho (negativo) |
| Link "ver completa"   | `--color-primary-500`, `font-weight: 500`, cursor pointer, hover underline |

#### 10.6.2 Resumo da IA (coluna direita)

- **Título**: "Resumo da IA" — `--font-size-xl`, `font-weight: 600`
- **Container**: `glass-card`, centralizado verticalmente

```
┌───────────────────────────────┐
│        Resumo da IA           │
│                               │
│           ✅                  │  ← Ícone grande (64px)
│                               │
│  Nenhum sinal de risco        │  ← Título do resumo
│     identificado              │
│                               │
│  Todos os indicadores estão   │  ← Texto descritivo
│  dentro dos parâmetros        │
│  esperados para um parto      │
│  seguro.                      │
│                               │
│  Ver detalhes da análise →    │  ← Link para análise
└───────────────────────────────┘
```

| Cenário               | Ícone              | Cor de fundo (sutil)                 | Título                             |
|-----------------------|--------------------|--------------------------------------|------------------------------------|
| Sem risco             | `check_circle`     | `rgba(16, 185, 129, 0.1)` (verde)   | Nenhum sinal de risco identificado |
| Risco moderado        | `warning`          | `rgba(245, 158, 11, 0.1)` (âmbar)   | Atenção: indicadores moderados     |
| Risco crítico         | `error`            | `rgba(239, 68, 68, 0.1)` (vermelho) | Risco crítico identificado         |

- Ícone: `64px`, cor correspondente ao nível de risco
- Título do resumo: `--font-size-lg`, `font-weight: 600`
- Descrição: `--font-size-sm`, cor `--color-text-muted`, `text-align: center`
- Link: `--color-primary-500`, `font-weight: 500`

---

### 10.7 Ações Rápidas

> Barra de ações no rodapé do conteúdo, antes do footer.

- **Título**: "Ações rápidas" — `--font-size-xl`, `font-weight: 600`
- **Layout**: `display: flex; gap: 16px; flex-wrap: wrap`

```
┌──────────────────────────────────────────────────────────────────────┐
│  Ações rápidas                                                       │
│                                                                      │
│  [📹 Ver vídeo ao vivo]  [📄 Gerar relatório]  [🔍 Avaliar caso]   │
│  [📝 Observação]  [📋 Histórico do paciente]                        │
└──────────────────────────────────────────────────────────────────────┘
```

| Ação                    | Ícone             | Variante                          |
|-------------------------|-------------------|-----------------------------------|
| Ver vídeo ao vivo       | `videocam`        | Outlined, hover `--color-primary-500` |
| Gerar relatório         | `description`     | Outlined, hover `--color-primary-500` |
| Avaliar caso            | `rate_review`     | Outlined, hover `--color-primary-500` |
| Observação              | `edit_note`       | Outlined, hover `--color-primary-500` |
| Histórico do paciente   | `history`         | Outlined, hover `--color-primary-500` |

**Estilo dos botões**:
- `glass-card` com padding `16px 24px`
- `display: flex; align-items: center; gap: 8px`
- Border: `1px solid --color-border`
- Ícone: `--color-text-muted`, transição para `--color-primary-500` no hover
- Texto: `--font-size-sm`, `font-weight: 500`
- Hover: `border-color: --color-primary-500`, `transform: translateY(-2px)`, `box-shadow: --shadow-glow-primary`

---

### 10.8 Footer

- **Texto**: "GuardIA Parto Seguro © 2025 • Todos os direitos reservados"
- **Estilo**: `--font-size-xs`, cor `--color-text-subtle`, `text-align: center`, `padding: 24px 0`

---

*Documento baseado na identidade visual atual (frontend/app.py) e adaptado para Angular Material.*
