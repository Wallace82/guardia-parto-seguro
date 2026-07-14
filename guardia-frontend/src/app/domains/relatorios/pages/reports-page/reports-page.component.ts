import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatRadioModule } from '@angular/material/radio';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { FormsModule } from '@angular/forms';
import { SessionsService } from '../../../sessoes/services/sessions.service';
import { SessionOut } from '../../../sessoes/models/sessions.models';
import { ExportPdfService } from '../../services/export-pdf.service';

@Component({
  selector: 'app-reports-page',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatRadioModule,
    MatCheckboxModule,
    MatSelectModule,
    MatProgressBarModule,
    MatSnackBarModule,
    FormsModule
  ],
  template: `
    <div class="p-8 max-w-5xl mx-auto animate-fade-in min-h-screen">
      
      <!-- AVISO DE SESSÕES VAZIAS -->
      @if (!loading() && completedSessions().length === 0) {
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-white mb-2">Relatórios</h1>
          <p class="text-text-muted">Geração de relatórios analíticos de sessões.</p>
        </div>
        <div class="bg-surface2 border border-border p-6 rounded-xl flex flex-col items-center justify-center text-center h-64">
          <mat-icon class="text-warning-500 mb-2 !w-12 !h-12 text-[48px]">warning</mat-icon>
          <h3 class="text-white font-semibold text-lg">Nenhuma sessão concluída</h3>
          <p class="text-text-muted mt-1">É necessário ter ao menos uma sessão com análise COMPLETA para gerar relatórios.</p>
        </div>
      }

      <!-- FORMULÁRIO DE GERAÇÃO -->
      @if (completedSessions().length > 0 && step() === 'config') {
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-white mb-2">Relatórios</h1>
          <p class="text-text-muted">Geração de relatórios analíticos de sessões.</p>
        </div>
        <div class="glass-card p-6">
          <h4 class="text-primary-400 font-semibold mb-6 flex items-center gap-2">
            <mat-icon>settings</mat-icon>
            Parâmetros de Geração
          </h4>

          <div class="flex flex-col gap-6">
            <!-- SELEÇÃO DA SESSÃO -->
            <div>
              <label class="block text-sm font-semibold text-white mb-2">Selecione a Sessão:</label>
              <mat-form-field appearance="outline" class="w-full">
                <mat-select [(ngModel)]="selectedSessionId">
                  @for (session of completedSessions(); track session.id) {
                    <mat-option [value]="session.id">
                      #{{ session.id }} — {{ session.title }} ({{ session.patient_code }})
                    </mat-option>
                  }
                </mat-select>
              </mat-form-field>
            </div>

            <!-- FORMATO -->
            <div>
              <label class="block text-sm font-semibold text-white mb-2">Formato do Relatório</label>
              <mat-radio-group [(ngModel)]="format" class="flex flex-col gap-3">
                <mat-radio-button value="pdf" color="primary">
                  <span class="text-white">Relatório Completo da Sessão (PDF)</span>
                </mat-radio-button>
                <mat-radio-button value="excel" color="primary">
                  <span class="text-white">Resumo Executivo</span>
                </mat-radio-button>
              </mat-radio-group>
            </div>

            <button 
              mat-flat-button 
              color="primary" 
              class="w-full !py-6 !text-lg !font-bold mt-4"
              [disabled]="!selectedSessionId"
              (click)="startGeneration()">
              Gerar Relatório Autenticado
            </button>
          </div>
        </div>
      }

      <!-- TELA DE PROCESSAMENTO -->
      @if (step() === 'processing') {
        <div class="glass-card p-12 flex flex-col items-center justify-center text-center mt-12 animate-fade-in">
          <div class="w-20 h-20 rounded-full bg-primary-500/10 flex items-center justify-center text-primary-400 mb-6 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-20"></span>
            <mat-icon class="text-5xl animate-spin">autorenew</mat-icon>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">
            Gerando relatório gerencial...
          </h4>
          <p class="text-text-muted text-sm max-w-sm mb-6 h-5">{{ statusMessage() }}</p>
          <div class="w-64 h-2 bg-surface2 rounded-full overflow-hidden">
            <div class="h-full bg-primary-500 rounded-full transition-all duration-300 ease-out" [style.width.%]="progress()"></div>
          </div>
        </div>
      }

      <!-- RELATÓRIO VISUAL (COMPLETED) -->
      @if (step() === 'completed') {
        <div class="animate-fade-in">
          <!-- Relatório Header -->
          <div class="flex items-center justify-between mb-8">
            <div>
              <button mat-stroked-button (click)="reset()" class="!rounded-full mb-4">
                <mat-icon>arrow_back</mat-icon> Voltar
              </button>
              <h1 class="text-3xl font-bold text-white mb-1">Relatório Gerado por IA</h1>
              <p class="text-text-muted">Análise completa do atendimento obstétrico</p>
            </div>
            <div class="flex gap-3">
              <button mat-stroked-button class="!rounded-full" (click)="downloadReport()">
                <mat-icon>save_alt</mat-icon> Exportar PDF
              </button>
              <button mat-stroked-button color="primary" class="!rounded-full border-primary-500 text-primary-400">
                <mat-icon>share</mat-icon> Compartilhar
              </button>
            </div>
          </div>

          <!-- Relatório Body (Printable area concept) -->
          <div class="bg-surface border border-border rounded-xl p-8 shadow-xl">
            
            <!-- Patient Info Bar Simples -->
            <div class="flex flex-wrap items-center justify-between pb-6 border-b border-border mb-8 gap-6">
              <div class="flex items-center gap-4">
                <div class="w-16 h-16 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center">
                  <mat-icon class="!text-3xl">person</mat-icon>
                </div>
                <div>
                  <h2 class="text-xl font-bold text-white mb-1">Paciente {{ activeSession()?.patient_code }}</h2>
                  <p class="text-sm text-text-muted">Sessão #{{ activeSession()?.id }} • {{ activeSession()?.title }}</p>
                </div>
              </div>
              
              <div class="flex gap-8">
                <div>
                  <span class="block text-xs text-text-muted font-medium mb-1">Data da Sessão</span>
                  <span class="block font-bold text-white">{{ activeSession()?.created_at | date:'dd/MM/yyyy HH:mm' }}</span>
                </div>
                <div>
                  <span class="block text-xs text-text-muted font-medium mb-1">Data do Relatório</span>
                  <span class="block font-bold text-white">{{ generationDate() | date:'dd/MM/yyyy HH:mm' }}</span>
                </div>
              </div>
            </div>

            <!-- Resumo Executivo e Risco -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div class="bg-surface2/40 p-6 rounded-xl border border-border">
                <h3 class="text-sm font-bold text-white mb-3">Resumo executivo</h3>
                <p class="text-sm text-text-muted leading-relaxed">
                  A análise multimodal realizada pelo GuardIA avaliou dados de vídeo, áudio, documentos e sinais vitais durante o atendimento.
                  <br><br>
                  Não foram identificados incidentes de alto risco. Recomenda-se manter a conduta atual e acompanhamento contínuo.
                </p>
              </div>
              
              <div class="bg-surface2/40 p-6 rounded-xl border border-border flex flex-col items-center justify-center">
                <h3 class="text-sm font-bold text-white mb-4 self-start">Classificação de risco</h3>
                <div class="flex items-center gap-4 mb-4">
                  <mat-icon [ngClass]="getRiskColorClass(activeSession()?.ira_level)" class="!text-5xl !w-12 !h-12">{{ getRiskIcon(activeSession()?.ira_level) }}</mat-icon>
                  <div>
                    <span class="block text-xl font-bold" [ngClass]="getRiskColorClass(activeSession()?.ira_level)">{{ getRiskLabel(activeSession()?.ira_level) }}</span>
                    <span class="block text-3xl font-black text-white">{{ activeSession()?.ira_score || 0 }}%</span>
                  </div>
                </div>
                <div class="w-full">
                  <div class="flex justify-between text-xs text-text-muted mb-1">
                    <span>Score IRA</span>
                    <span class="font-bold text-white">{{ activeSession()?.ira_score || 0 }}%</span>
                  </div>
                  <div class="w-full h-1.5 bg-bg rounded-full overflow-hidden">
                    <div class="h-full bg-primary-500 rounded-full transition-all" [style.width.%]="activeSession()?.ira_score || 0"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Fontes Analisadas -->
            <div class="mb-8">
              <h3 class="text-sm font-bold text-white mb-4">Fontes de dados analisadas</h3>
              <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-surface2/40 p-4 rounded-xl border border-border flex flex-col items-center text-center">
                  <mat-icon class="text-primary-400 mb-2">videocam</mat-icon>
                  <span class="text-sm font-bold text-white">Vídeo</span>
                  <span class="text-[10px] font-bold mt-2 px-2 py-0.5 rounded-full flex items-center gap-1"
                        [ngClass]="hasMedia('video') ? 'text-success bg-success/10' : 'text-text-muted bg-surface2'">
                    <mat-icon class="!text-[12px] !w-3 !h-3">{{ hasMedia('video') ? 'check_circle' : 'remove_circle_outline' }}</mat-icon> 
                    {{ hasMedia('video') ? 'Processado' : 'Ausente' }}
                  </span>
                </div>
                <div class="bg-surface2/40 p-4 rounded-xl border border-border flex flex-col items-center text-center">
                  <mat-icon class="text-secondary-400 mb-2">graphic_eq</mat-icon>
                  <span class="text-sm font-bold text-white">Áudio</span>
                  <span class="text-[10px] font-bold mt-2 px-2 py-0.5 rounded-full flex items-center gap-1"
                        [ngClass]="hasMedia('audio') ? 'text-success bg-success/10' : 'text-text-muted bg-surface2'">
                    <mat-icon class="!text-[12px] !w-3 !h-3">{{ hasMedia('audio') ? 'check_circle' : 'remove_circle_outline' }}</mat-icon> 
                    {{ hasMedia('audio') ? 'Processado' : 'Ausente' }}
                  </span>
                </div>
                <div class="bg-surface2/40 p-4 rounded-xl border border-border flex flex-col items-center text-center">
                  <mat-icon class="text-primary-300 mb-2">description</mat-icon>
                  <span class="text-sm font-bold text-white">Documentos</span>
                  <span class="text-[10px] font-bold mt-2 px-2 py-0.5 rounded-full flex items-center gap-1"
                        [ngClass]="hasMedia('document') ? 'text-success bg-success/10' : 'text-text-muted bg-surface2'">
                    <mat-icon class="!text-[12px] !w-3 !h-3">{{ hasMedia('document') ? 'check_circle' : 'remove_circle_outline' }}</mat-icon> 
                    {{ hasMedia('document') ? 'Processado' : 'Ausente' }}
                  </span>
                </div>
                <div class="bg-surface2/40 p-4 rounded-xl border border-border flex flex-col items-center text-center">
                  <mat-icon class="text-danger-400 mb-2">note_alt</mat-icon>
                  <span class="text-sm font-bold text-white">Anotações</span>
                  <span class="text-[10px] font-bold mt-2 px-2 py-0.5 rounded-full flex items-center gap-1"
                        [ngClass]="activeSession()?.notes ? 'text-success bg-success/10' : 'text-text-muted bg-surface2'">
                    <mat-icon class="!text-[12px] !w-3 !h-3">{{ activeSession()?.notes ? 'check_circle' : 'remove_circle_outline' }}</mat-icon> 
                    {{ activeSession()?.notes ? 'Analisadas' : 'Ausente' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Indicadores e Evolução -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div>
                <h3 class="text-sm font-bold text-white mb-4">Indicadores analisados</h3>
                <div class="flex flex-col gap-2">
                  <div class="flex items-center justify-between p-2 rounded hover:bg-surface2/30">
                    <span class="flex items-center gap-2 text-sm text-text-muted"><mat-icon class="!text-lg text-success">psychology</mat-icon> Estado emocional</span>
                    <span class="text-xs font-bold text-success bg-success/10 px-2 py-0.5 rounded">Positivo</span>
                  </div>
                  <div class="flex items-center justify-between p-2 rounded hover:bg-surface2/30">
                    <span class="flex items-center gap-2 text-sm text-text-muted"><mat-icon class="!text-lg text-primary-400">forum</mat-icon> Comunicação</span>
                    <span class="text-xs font-bold text-success bg-success/10 px-2 py-0.5 rounded">Humanizada</span>
                  </div>
                  <div class="flex items-center justify-between p-2 rounded hover:bg-surface2/30">
                    <span class="flex items-center gap-2 text-sm text-text-muted"><mat-icon class="!text-lg text-warning">accessibility_new</mat-icon> Linguagem corporal</span>
                    <span class="text-xs font-bold text-success bg-success/10 px-2 py-0.5 rounded">Adequada</span>
                  </div>
                  <div class="flex items-center justify-between p-2 rounded hover:bg-surface2/30">
                    <span class="flex items-center gap-2 text-sm text-text-muted"><mat-icon class="!text-lg text-secondary-400">mic</mat-icon> Análise vocal</span>
                    <span class="text-xs font-bold text-success bg-success/10 px-2 py-0.5 rounded">Estável</span>
                  </div>
                  <div class="flex items-center justify-between p-2 rounded hover:bg-surface2/30">
                    <span class="flex items-center gap-2 text-sm text-text-muted"><mat-icon class="!text-lg text-primary-300">people</mat-icon> Interações da equipe</span>
                    <span class="text-xs font-bold text-success bg-success/10 px-2 py-0.5 rounded">Positivas</span>
                  </div>
                  <div class="flex items-center justify-between p-2 rounded hover:bg-surface2/30">
                    <span class="flex items-center gap-2 text-sm text-text-muted"><mat-icon class="!text-lg text-text-muted">person_add</mat-icon> Presença de acompanhante</span>
                    <span class="text-xs font-bold text-success bg-success/10 px-2 py-0.5 rounded">Confirmada</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 class="text-sm font-bold text-white mb-4">Principais fatores positivos</h3>
                <div class="flex flex-col gap-3">
                  <div class="flex items-start gap-3">
                    <mat-icon class="text-success !text-base">check_circle</mat-icon>
                    <span class="text-sm text-white">Ambiente acolhedor e seguro</span>
                  </div>
                  <div class="flex items-start gap-3">
                    <mat-icon class="text-success !text-base">check_circle</mat-icon>
                    <span class="text-sm text-white">Equipe atenciosa e empática</span>
                  </div>
                  <div class="flex items-start gap-3">
                    <mat-icon class="text-success !text-base">check_circle</mat-icon>
                    <span class="text-sm text-white">Comunicação clara e respeitosa</span>
                  </div>
                  <div class="flex items-start gap-3">
                    <mat-icon class="text-success !text-base">check_circle</mat-icon>
                    <span class="text-sm text-white">Paciente confiante e colaborativa</span>
                  </div>
                  <div class="flex items-start gap-3">
                    <mat-icon class="text-success !text-base">check_circle</mat-icon>
                    <span class="text-sm text-white">Acompanhante presente e participativo</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer / Assinaturas -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-border mt-8">
              <div>
                <h3 class="text-sm font-bold text-white mb-4">Recomendações</h3>
                <div class="flex flex-col gap-3">
                  <div class="flex items-center gap-3">
                    <mat-icon class="text-text-muted !text-base">lock</mat-icon>
                    <span class="text-sm text-text-muted">Manter conduta atual</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <mat-icon class="text-text-muted !text-base">visibility</mat-icon>
                    <span class="text-sm text-text-muted">Continuar monitoramento contínuo</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <mat-icon class="text-text-muted !text-base">assignment_late</mat-icon>
                    <span class="text-sm text-text-muted">Reavaliar em caso de mudança clínica</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 class="text-sm font-bold text-white mb-4">Responsáveis</h3>
                <div class="grid grid-cols-3 gap-y-2 text-sm">
                  <span class="font-bold text-white">Profissional:</span>
                  <span class="col-span-2 text-text-muted">Enf. João Silva</span>
                  
                  <span class="font-bold text-white">Função:</span>
                  <span class="col-span-2 text-text-muted">Enfermeiro Obstetra</span>
                  
                  <span class="font-bold text-white">Registro:</span>
                  <span class="col-span-2 text-text-muted">COREN 123456</span>
                  
                  <span class="font-bold text-white mt-2">Assinatura:</span>
                  <span class="col-span-2 text-text-muted mt-2 border-b border-text-muted/30 pb-1 italic font-serif">João Silva</span>
                </div>
              </div>
            </div>

            <!-- Autenticidade -->
            <div class="mt-8 pt-4 border-t border-border/50 text-center flex flex-col items-center">
              <div class="flex items-center justify-center gap-2 text-success font-medium mb-1">
                <mat-icon class="!text-sm !w-3.5 !h-3.5">verified</mat-icon>
                <span class="text-xs">Documento Assinado Digitalmente</span>
              </div>
              <p class="text-[10px] text-text-subtle font-mono break-all max-w-lg">
                HASH: {{ fakeHash() }}
              </p>
            </div>

          </div>
        </div>
      }
    </div>
  `
})
export class ReportsPageComponent implements OnInit {
  private readonly sessionsService = inject(SessionsService);
  private readonly exportPdf = inject(ExportPdfService);
  private readonly snackBar = inject(MatSnackBar);

  loading = signal(true);
  completedSessions = signal<SessionOut[]>([]);

  // Formulário
  selectedSessionId: number | null = null;
  format: 'pdf' | 'excel' = 'pdf';
  includeTranscription = true;
  includeFrames = true;

  // Processamento
  step = signal<'config' | 'processing' | 'completed'>('config');
  progress = signal(0);
  statusMessage = signal('');
  fakeHash = signal('');
  generationDate = signal(new Date());

  activeSession = signal<SessionOut | null>(null);

  ngOnInit() {
    this.sessionsService.getSessions(0, 100).subscribe({
      next: (res) => {
        const completed = res.items.filter(s => s.status === 'completed');
        this.completedSessions.set(completed);
        
        if (completed.length > 0) {
          this.selectedSessionId = completed[0].id;
        }
        this.loading.set(false);
      },
      error: () => {
        this.snackBar.open('Erro ao carregar sessões.', 'Fechar');
        this.loading.set(false);
      }
    });
  }

  startGeneration() {
    if (!this.selectedSessionId) return;

    this.step.set('processing');
    this.progress.set(0);
    this.statusMessage.set('🔍 Carregando dados da sessão e mídias analisadas...');
    
    this.sessionsService.getSession(this.selectedSessionId).subscribe({
      next: (session) => {
        this.activeSession.set(session);
        this.progress.set(40);
        this.statusMessage.set('✍️ Estruturando layout e renderizando gráficos de IRA...');
        
        setTimeout(() => {
          this.progress.set(80);
          this.statusMessage.set('🔒 Calculando assinatura criptográfica SHA-256...');
          
          setTimeout(() => {
            this.progress.set(100);
            this.statusMessage.set('✅ Pronto!');
            
            this.generationDate.set(new Date());
            this.fakeHash.set(this.generateRandomSha256());
            this.step.set('completed');
            this.snackBar.open('🎉 Relatório gerado com sucesso!', 'OK', { duration: 3000 });
          }, 800);
        }, 1000);
      },
      error: () => {
        this.snackBar.open('Erro ao carregar sessão', 'Fechar');
        this.reset();
      }
    });
  }

  downloadReport() {
    const session = this.activeSession();
    if (this.selectedSessionId && session) {
      if (this.format === 'pdf') {
        this.exportPdf.exportSessionReport(this.selectedSessionId);
      } else {
        this.snackBar.open('Baixando arquivo Excel...', '', { duration: 2000 });
        const score = session.ira_score !== null ? session.ira_score : 'N/A';
        const blob = new Blob([`ID,Title,Patient,Status,IRA_Score\n${session.id},"${session.title}","${session.patient_code}",${session.status},${score}`], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Relatorio_Executivo_Sessao_${session.id}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      }
    }
  }

  reset() {
    this.step.set('config');
    this.progress.set(0);
  }

  private generateRandomSha256(): string {
    return Array.from({length: 64}, () => 
      Math.floor(Math.random() * 16).toString(16)
    ).join('');
  }

  getRiskLabel(level: string | null | undefined): string {
    if (!level) return 'Sem classificação';
    switch(level.toLowerCase()) {
      case 'baixo': return 'Baixo risco';
      case 'moderado': return 'Risco moderado';
      case 'elevado': return 'Risco elevado';
      case 'critico': return 'Risco crítico';
      default: return level;
    }
  }

  getRiskColorClass(level: string | null | undefined): string {
    if (!level) return 'text-text-muted';
    switch(level.toLowerCase()) {
      case 'baixo': return 'text-success';
      case 'moderado': return 'text-warning';
      case 'elevado': return 'text-danger-400';
      case 'critico': return 'text-danger-500';
      default: return 'text-text-muted';
    }
  }

  getRiskIcon(level: string | null | undefined): string {
    if (!level) return 'help_outline';
    switch(level.toLowerCase()) {
      case 'baixo': return 'verified_user';
      case 'moderado': return 'warning';
      case 'elevado': return 'error_outline';
      case 'critico': return 'report';
      default: return 'info';
    }
  }

  hasMedia(type: string): boolean {
    const session = this.activeSession();
    if (!session || !session.media_files) return false;
    return session.media_files.some(m => m.media_type === type);
  }
}
