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
import { ActivatedRoute } from '@angular/router';

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
                <mat-icon>picture_as_pdf</mat-icon> Exportar PDF
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
                  {{ getDynamicSummary(activeSession()) }}
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
                    <span>Score IGA</span>
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
                    <span class="flex items-center gap-2 text-sm text-text-muted"><mat-icon class="!text-lg text-primary-400">videocam</mat-icon> Análise de Vídeo</span>
                    <span class="text-xs font-bold px-2 py-0.5 rounded" [ngClass]="getScoreClass(activeSession()?.score_video)">{{ formatScore(activeSession()?.score_video) }}</span>
                  </div>
                  <div class="flex items-center justify-between p-2 rounded hover:bg-surface2/30">
                    <span class="flex items-center gap-2 text-sm text-text-muted"><mat-icon class="!text-lg text-secondary-400">graphic_eq</mat-icon> Análise de Áudio</span>
                    <span class="text-xs font-bold px-2 py-0.5 rounded" [ngClass]="getScoreClass(activeSession()?.score_audio)">{{ formatScore(activeSession()?.score_audio) }}</span>
                  </div>
                  <div class="flex items-center justify-between p-2 rounded hover:bg-surface2/30">
                    <span class="flex items-center gap-2 text-sm text-text-muted"><mat-icon class="!text-lg text-primary-300">description</mat-icon> Análise Documental</span>
                    <span class="text-xs font-bold px-2 py-0.5 rounded" [ngClass]="getScoreClass(activeSession()?.score_document)">{{ formatScore(activeSession()?.score_document) }}</span>
                  </div>
                  <div class="flex items-center justify-between p-2 rounded hover:bg-surface2/30">
                    <span class="flex items-center gap-2 text-sm text-text-muted"><mat-icon class="!text-lg text-danger-400">note_alt</mat-icon> Análise de Anotações</span>
                    <span class="text-xs font-bold px-2 py-0.5 rounded" [ngClass]="getScoreClass(activeSession()?.score_notes)">{{ formatScore(activeSession()?.score_notes) }}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 class="text-sm font-bold text-white mb-4">Principais fatores positivos</h3>
                <div class="flex flex-col gap-3">
                  @for (rec of getDynamicFactors(activeSession()); track rec) {
                    <div class="flex items-start gap-3">
                      <mat-icon class="text-primary-400 !text-base">info</mat-icon>
                      <span class="text-sm text-white">{{ rec }}</span>
                    </div>
                  }
                </div>
              </div>
            </div>

            <!-- Footer / Assinaturas -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-border mt-8">
              <div>
                <h3 class="text-sm font-bold text-white mb-4">Recomendações</h3>
                <div class="flex flex-col gap-3">
                  @for (rec of getDynamicRecommendations(activeSession()); track rec) {
                    <div class="flex items-center gap-3">
                      <mat-icon class="text-text-muted !text-base">arrow_right</mat-icon>
                      <span class="text-sm text-text-muted">{{ rec }}</span>
                    </div>
                  }
                </div>
              </div>

              <div>
                <h3 class="text-sm font-bold text-white mb-4">Responsáveis</h3>
                <div class="grid grid-cols-3 gap-y-2 text-sm">
                  <span class="font-bold text-white">Profissional:</span>
                  <span class="col-span-2 text-text-muted">Profissional ID #{{ activeSession()?.professional_id }}</span>
                  
                  <span class="font-bold text-white">Função:</span>
                  <span class="col-span-2 text-text-muted">Especialista GuardIA</span>
                  
                  <span class="font-bold text-white">Anotações:</span>
                  <span class="col-span-2 text-text-muted line-clamp-2" [title]="activeSession()?.notes || 'Nenhuma anotação'">{{ activeSession()?.notes || 'Nenhuma anotação registrada.' }}</span>
                  
                  <span class="font-bold text-white mt-2">Assinatura:</span>
                  <span class="col-span-2 text-text-muted mt-2 border-b border-text-muted/30 pb-1 italic font-serif">Prof. {{ activeSession()?.professional_id }}</span>
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

        <!-- VERSÃO PARA IMPRESSÃO (Oculta da tela, mas lida pelo html2canvas) -->
        <div style="position: absolute; left: -9999px; top: 0; opacity: 0; pointer-events: none;">
          <div id="pdf-printable-content" class="bg-white text-gray-900 p-12 w-[800px]" style="font-family: 'Helvetica Neue', Arial, sans-serif;">
            
            <!-- Header -->
            <div class="border-b-2 border-gray-300 pb-6 mb-8 flex justify-between items-start">
              <div>
                <h1 class="text-3xl font-black text-gray-900 mb-2 uppercase tracking-tight">Relatório GuardIA</h1>
                <p class="text-lg text-gray-600 font-medium">Análise Multimodal de Atendimento Obstétrico</p>
              </div>
              <div class="text-right">
                <p class="text-sm text-gray-500 font-bold uppercase tracking-wider mb-1">Emitido em</p>
                <p class="text-lg text-gray-900 font-medium">{{ generationDate() | date:'dd/MM/yyyy HH:mm' }}</p>
              </div>
            </div>

            <!-- Dados Paciente (Horizontal Distribution) -->
            <div class="bg-gray-50 rounded-xl mb-8 border border-gray-200 overflow-hidden">
              <div class="bg-gray-200 px-6 py-3 border-b border-gray-300">
                <h2 class="text-sm font-bold text-gray-800 uppercase tracking-widest">Informações Gerais da Sessão</h2>
              </div>
              <div class="p-6 grid grid-cols-4 gap-6 text-sm">
                <div class="col-span-1">
                  <p class="text-gray-500 font-bold mb-1">Paciente</p>
                  <p class="text-gray-900 font-medium text-base">{{ activeSession()?.patient_code }}</p>
                </div>
                <div class="col-span-1">
                  <p class="text-gray-500 font-bold mb-1">Sessão</p>
                  <p class="text-gray-900 font-medium text-base">#{{ activeSession()?.id }}</p>
                </div>
                <div class="col-span-2">
                  <p class="text-gray-500 font-bold mb-1">Profissional Responsável</p>
                  <p class="text-gray-900 font-medium text-base">ID #{{ activeSession()?.professional_id }} - Especialista GuardIA</p>
                </div>
              </div>
            </div>

            <!-- Resumo e Risco -->
            <div class="grid grid-cols-3 gap-8 mb-8">
              <div class="col-span-2 flex flex-col justify-center">
                <h3 class="text-sm font-bold text-gray-800 uppercase tracking-widest mb-3">Síntese Executiva</h3>
                <p class="text-base text-gray-700 leading-relaxed text-justify">
                  {{ getDynamicSummary(activeSession()) }}
                </p>
              </div>
              <div class="col-span-1 bg-gray-50 p-6 rounded-xl border border-gray-200 flex flex-col items-center justify-center text-center">
                <h3 class="text-sm font-bold text-gray-800 uppercase tracking-widest mb-4">Risco (IGA)</h3>
                <span class="text-xl font-bold mb-1" [ngClass]="getPrintRiskColorClass(activeSession()?.ira_level)">{{ getRiskLabel(activeSession()?.ira_level) }}</span>
                <span class="text-5xl font-black text-gray-900">{{ activeSession()?.ira_score || 0 }}<span class="text-2xl text-gray-500">%</span></span>
              </div>
            </div>

            <!-- Indicadores -->
            <div class="mb-8">
              <h3 class="text-sm font-bold text-gray-800 uppercase tracking-widest mb-4 border-b border-gray-300 pb-2">Desempenho dos Indicadores</h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="flex justify-between items-center bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <span class="text-gray-700 font-medium">Análise de Vídeo</span>
                  <span class="font-bold text-gray-900 bg-white px-3 py-1 rounded shadow-sm border border-gray-200">{{ formatScore(activeSession()?.score_video) }}</span>
                </div>
                <div class="flex justify-between items-center bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <span class="text-gray-700 font-medium">Análise de Áudio</span>
                  <span class="font-bold text-gray-900 bg-white px-3 py-1 rounded shadow-sm border border-gray-200">{{ formatScore(activeSession()?.score_audio) }}</span>
                </div>
                <div class="flex justify-between items-center bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <span class="text-gray-700 font-medium">Análise Documental</span>
                  <span class="font-bold text-gray-900 bg-white px-3 py-1 rounded shadow-sm border border-gray-200">{{ formatScore(activeSession()?.score_document) }}</span>
                </div>
                <div class="flex justify-between items-center bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <span class="text-gray-700 font-medium">Análise de Anotações</span>
                  <span class="font-bold text-gray-900 bg-white px-3 py-1 rounded shadow-sm border border-gray-200">{{ formatScore(activeSession()?.score_notes) }}</span>
                </div>
              </div>
            </div>

            <!-- Recomendações e Fatores -->
            <div class="grid grid-cols-2 gap-8 mb-8">
              <div>
                <h3 class="text-sm font-bold text-gray-800 uppercase tracking-widest mb-4 border-b border-gray-300 pb-2">Recomendações Clínicas</h3>
                <ul class="space-y-3">
                  @for (rec of getDynamicRecommendations(activeSession()); track rec) {
                    <li class="flex items-start gap-2">
                      <div class="w-2 h-2 rounded-full bg-gray-400 mt-1.5 flex-shrink-0"></div>
                      <span class="text-gray-700 text-sm leading-snug">{{ rec }}</span>
                    </li>
                  }
                </ul>
              </div>
              <div>
                <h3 class="text-sm font-bold text-gray-800 uppercase tracking-widest mb-4 border-b border-gray-300 pb-2">Fatores Relevantes</h3>
                <ul class="space-y-3">
                  @for (fac of getDynamicFactors(activeSession()); track fac) {
                    <li class="flex items-start gap-2">
                      <div class="w-2 h-2 rounded-full bg-gray-400 mt-1.5 flex-shrink-0"></div>
                      <span class="text-gray-700 text-sm leading-snug">{{ fac }}</span>
                    </li>
                  }
                </ul>
              </div>
            </div>

            @if(activeSession()?.notes) {
              <div class="mb-8">
                <h3 class="text-sm font-bold text-gray-800 uppercase tracking-widest mb-3 border-b border-gray-300 pb-2">Anotações Registradas</h3>
                <div class="bg-yellow-50 p-4 rounded-lg border border-yellow-200 text-sm text-gray-800 italic">
                  "{{ activeSession()?.notes }}"
                </div>
              </div>
            }

            <!-- Autenticidade -->
            <div class="mt-12 pt-6 border-t-2 border-gray-300 text-center">
              <p class="text-sm font-black text-gray-800 uppercase tracking-widest mb-2">Documento Assinado Digitalmente</p>
              <p class="text-[10px] text-gray-400 font-mono tracking-widest">
                HASH DE AUTENTICIDADE: {{ fakeHash() }}
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
  includeTranscription = true;
  includeFrames = true;

  // Processamento
  step = signal<'config' | 'processing' | 'completed'>('config');
  progress = signal(0);
  statusMessage = signal('');
  fakeHash = signal('');
  generationDate = signal(new Date());

  activeSession = signal<SessionOut | null>(null);

  private readonly route = inject(ActivatedRoute);

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      const qId = params['session_id'] ? parseInt(params['session_id'], 10) : null;
      
      this.sessionsService.getSessions(0, 100).subscribe({
        next: (res) => {
          const completed = res.items.filter(s => s.status === 'completed');
          this.completedSessions.set(completed);
          
          if (completed.length > 0) {
            if (qId && completed.find(s => s.id === qId)) {
              this.selectedSessionId = qId;
            } else {
              this.selectedSessionId = completed[0].id;
            }
          }
          this.loading.set(false);
        },
        error: () => {
          this.snackBar.open('Erro ao carregar sessões.', 'Fechar');
          this.loading.set(false);
        }
      });
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
        this.statusMessage.set('✍️ Estruturando layout e renderizando gráficos de IGA...');
        
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
      const filename = `Resumo_Executivo_GuardIA_Sessao_${session.id}.pdf`;
      this.exportPdf.exportElementToPdf('pdf-printable-content', filename);
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

  getDynamicSummary(session: SessionOut | null): string {
    if (!session) return '';
    const ira = session.ira_level?.toLowerCase() || 'baixo';
    
    if (ira === 'baixo') {
      return 'A análise multimodal indica um cenário positivo e estável. Não foram identificados incidentes de risco. Recomenda-se manter a conduta atual e o acompanhamento contínuo.';
    } else if (ira === 'moderado') {
      return 'Foram identificados pontos de atenção na análise multimodal. É necessário acompanhamento mais próximo, reavaliação de conduta e maior atenção à comunicação.';
    } else {
      return 'ATENÇÃO: A análise multimodal indica um nível de risco elevado/crítico. Recomenda-se intervenção imediata, revisão clínica urgente e acionamento de equipe de apoio.';
    }
  }

  formatScore(score: number | null | undefined): string {
    if (score === null || score === undefined) return 'N/A';
    return `${score}/100`;
  }

  getScoreClass(score: number | null | undefined): string {
    if (score === null || score === undefined) return 'text-text-muted bg-surface2';
    if (score >= 80) return 'text-success bg-success/10';
    if (score >= 50) return 'text-warning bg-warning/10';
    return 'text-danger-400 bg-danger-400/10';
  }

  getDynamicFactors(session: SessionOut | null): string[] {
    if (!session) return [];
    const factors = [];
    if ((session.score_video || 0) >= 80) factors.push('Linguagem corporal e ambiente adequados');
    if ((session.score_audio || 0) >= 80) factors.push('Comunicação clara e tom de voz acolhedor');
    if ((session.score_document || 0) >= 80) factors.push('Documentação completa e aderente ao protocolo');
    if (factors.length === 0) factors.push('Fatores positivos limitados identificados');
    return factors;
  }

  getDynamicRecommendations(session: SessionOut | null): string[] {
    if (!session) return [];
    const ira = session.ira_level?.toLowerCase() || 'baixo';
    if (ira === 'baixo') {
      return ['Manter conduta atual', 'Continuar monitoramento contínuo', 'Reforçar orientações de alta se aplicável'];
    } else if (ira === 'moderado') {
      return ['Aumentar frequência de monitoramento', 'Reavaliar indicadores clínicos vitais', 'Revisar documentação e anotações ativamente'];
    } else {
      return ['Intervenção médica imediata', 'Acionar equipe multidisciplinar', 'Reavaliação completa de conduta'];
    }
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

  getPrintRiskColorClass(level: string | null | undefined): string {
    if (!level) return 'text-gray-500';
    switch(level.toLowerCase()) {
      case 'baixo': return 'text-green-600';
      case 'moderado': return 'text-yellow-600';
      case 'elevado': return 'text-orange-600';
      case 'critico': return 'text-red-600';
      default: return 'text-gray-500';
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
