import { Component, signal, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSnackBar } from '@angular/material/snack-bar';
import { SettingsService, SystemSettings } from '../../services/settings.service';

@Component({
  selector: 'app-admin-settings-page',
  standalone: true,
  imports: [CommonModule, FormsModule, MatIconModule, MatButtonModule, MatSlideToggleModule],
  template: `
    <div class="p-8 max-w-[1200px] mx-auto min-h-screen flex flex-col gap-6">
      
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 class="text-3xl font-bold text-white mb-1 flex items-center gap-3">
            <mat-icon class="text-primary-500 text-3xl">settings</mat-icon>
            Configurações Globais
          </h1>
          <p class="text-text-muted">Área restrita. Ajuste os parâmetros de funcionamento do sistema GuardIA.</p>
        </div>
        
        <div class="flex gap-3">
          <button mat-flat-button color="primary" (click)="saveSettings()" [disabled]="isSaving()">
            <mat-icon *ngIf="!isSaving()">save</mat-icon>
            <mat-icon *ngIf="isSaving()"><span class="animate-spin material-icons">autorenew</span></mat-icon>
            Salvar Alterações
          </button>
        </div>
      </div>

      <!-- Settings Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-slide-up">
        
        <!-- Notificações -->
        <div class="glass-card p-6 flex flex-col gap-6">
          <div class="flex items-center gap-3 border-b border-border/50 pb-4">
            <div class="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center text-primary-400">
              <mat-icon>notifications_active</mat-icon>
            </div>
            <div>
              <h2 class="text-lg font-bold text-white m-0">Notificações de Alerta</h2>
              <p class="text-sm text-text-muted m-0">Gerencie como o sistema avisa sobre alertas críticos.</p>
            </div>
          </div>
          
          <div class="flex flex-col gap-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-white font-medium mb-1">E-mails de Alertas Críticos</p>
                <p class="text-xs text-text-muted">Disparar e-mails imediatamente ao detectar um risco alto.</p>
              </div>
              <mat-slide-toggle [checked]="settings().email_alerts" (change)="updateSetting('email_alerts', $event.checked)" color="primary"></mat-slide-toggle>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <p class="text-white font-medium mb-1">Notificações Push no Navegador</p>
                <p class="text-xs text-text-muted">Enviar pop-ups para profissionais conectados.</p>
              </div>
              <mat-slide-toggle [checked]="settings().push_notifications" (change)="updateSetting('push_notifications', $event.checked)" color="primary"></mat-slide-toggle>
            </div>
          </div>
        </div>

        <!-- Análise de IA -->
        <div class="glass-card p-6 flex flex-col gap-6">
          <div class="flex items-center gap-3 border-b border-border/50 pb-4">
            <div class="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center text-success">
              <mat-icon>psychology</mat-icon>
            </div>
            <div>
              <h2 class="text-lg font-bold text-white m-0">Motor de Inteligência</h2>
              <p class="text-sm text-text-muted m-0">Parâmetros de avaliação do modelo de IA (Fusion).</p>
            </div>
          </div>
          
          <div class="flex flex-col gap-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-white font-medium mb-1">Modo de Avaliação Estrita</p>
                <p class="text-xs text-text-muted">Aumenta a sensibilidade para marcação de riscos.</p>
              </div>
              <mat-slide-toggle [checked]="settings().strict_mode" (change)="updateSetting('strict_mode', $event.checked)" color="primary"></mat-slide-toggle>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <p class="text-white font-medium mb-1">Auto-processar Áudios</p>
                <p class="text-xs text-text-muted">Transcrever e analisar automaticamente após o upload.</p>
              </div>
              <mat-slide-toggle [checked]="settings().auto_process_audio" (change)="updateSetting('auto_process_audio', $event.checked)" color="primary"></mat-slide-toggle>
            </div>
          </div>
        </div>

        <!-- Segurança e Retenção -->
        <div class="glass-card p-6 flex flex-col gap-6 lg:col-span-2">
          <div class="flex items-center gap-3 border-b border-border/50 pb-4">
            <div class="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center text-warning">
              <mat-icon>security</mat-icon>
            </div>
            <div>
              <h2 class="text-lg font-bold text-white m-0">Segurança & Retenção de Dados</h2>
              <p class="text-sm text-text-muted m-0">Gerencie a política de expiração de dados da plataforma.</p>
            </div>
          </div>
          
          <div class="flex flex-col md:flex-row gap-6">
            <div class="flex-1 bg-surface2/30 border border-border rounded-xl p-4">
              <p class="text-xs text-text-muted font-bold uppercase tracking-wider mb-2">Retenção de Prontuários</p>
              <div class="flex items-center gap-3">
                <input type="number" [value]="settings().retention_days" (change)="updateNumber('retention_days', $event)" 
                       class="w-24 bg-surface border border-border rounded-lg py-2 px-3 text-white focus:outline-none focus:border-primary-500 text-center font-bold">
                <span class="text-white">Dias</span>
              </div>
              <p class="text-xs text-text-muted mt-2">Após este período, os dados da sessão serão anonimizados.</p>
            </div>

            <div class="flex-1 bg-surface2/30 border border-border rounded-xl p-4">
              <p class="text-xs text-text-muted font-bold uppercase tracking-wider mb-2">Tempo Limite de Sessão (Inatividade)</p>
              <div class="flex items-center gap-3">
                <input type="number" [value]="settings().timeout_minutes" (change)="updateNumber('timeout_minutes', $event)" 
                       class="w-24 bg-surface border border-border rounded-lg py-2 px-3 text-white focus:outline-none focus:border-primary-500 text-center font-bold">
                <span class="text-white">Minutos</span>
              </div>
              <p class="text-xs text-text-muted mt-2">Desconectar usuários automaticamente se inativos.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class AdminSettingsPageComponent implements OnInit {
  private readonly snackBar = inject(MatSnackBar);
  private readonly settingsService = inject(SettingsService);

  isSaving = signal(false);
  isLoading = signal(true);
  
  settings = signal<SystemSettings>({
    email_alerts: true,
    push_notifications: false,
    strict_mode: true,
    auto_process_audio: true,
    retention_days: 180,
    timeout_minutes: 30
  });

  ngOnInit() {
    this.settingsService.getSettings().subscribe({
      next: (data) => {
        this.settings.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.snackBar.open('Erro ao carregar configurações', 'Fechar', { duration: 3000 });
        this.isLoading.set(false);
      }
    });
  }

  updateSetting(key: keyof SystemSettings, value: boolean) {
    this.settings.update(s => ({ ...s, [key]: value }));
  }

  updateNumber(key: keyof SystemSettings, event: Event) {
    const value = parseInt((event.target as HTMLInputElement).value, 10);
    if (!isNaN(value)) {
      this.settings.update(s => ({ ...s, [key]: value }));
    }
  }

  saveSettings() {
    this.isSaving.set(true);
    this.settingsService.updateSettings(this.settings()).subscribe({
      next: (data) => {
        this.settings.set(data);
        this.isSaving.set(false);
        this.snackBar.open('Configurações salvas com sucesso!', 'OK', {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
      },
      error: () => {
        this.isSaving.set(false);
        this.snackBar.open('Erro ao salvar configurações', 'Fechar', { duration: 3000 });
      }
    });
  }
}
