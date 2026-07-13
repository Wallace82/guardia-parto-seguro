import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { SessionOut } from '../../sessoes/models/sessions.models';

@Component({
  selector: 'app-patient-info-bar',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="glass-card p-6 flex flex-wrap items-center gap-6 animate-fade-in">
      <!-- Avatar -->
      <div class="w-20 h-20 rounded-full border-[3px] border-primary-500 bg-primary-500/20 flex items-center justify-center flex-shrink-0 overflow-hidden">
        <mat-icon class="!text-4xl text-primary-400">person</mat-icon>
      </div>

      <!-- Patient Info -->
      <div class="flex-1 min-w-[200px]">
        <h2 class="text-xl font-semibold text-white mb-1">{{ patientName() }}</h2>
        <p class="text-sm text-text-muted">{{ clinicalDetails() }}</p>
      </div>

      <!-- Sala / Leito -->
      <div class="flex items-center gap-6">
        <div class="text-center">
          <span class="block text-xs text-text-subtle uppercase tracking-wider font-medium">Sala</span>
          <span class="block text-2xl font-bold text-white">{{ sala() }}</span>
        </div>
        <div class="w-px h-10 bg-border"></div>
        <div class="text-center">
          <span class="block text-xs text-text-subtle uppercase tracking-wider font-medium">Leito</span>
          <span class="block text-2xl font-bold text-white">{{ leito() }}</span>
        </div>
      </div>

      <!-- Separator -->
      <div class="w-px h-10 bg-border hidden lg:block"></div>

      <!-- Início TP -->
      <div class="text-center min-w-[140px]">
        <span class="block text-xs text-text-subtle uppercase tracking-wider font-medium">Início do trabalho de parto</span>
        <span class="block text-lg font-bold text-white mt-1">{{ startTime() }}</span>
        <span class="block text-xs text-text-muted">{{ elapsedTime() }}</span>
      </div>

      <!-- Separator -->
      <div class="w-px h-10 bg-border hidden lg:block"></div>

      <!-- Status IA -->
      <div class="flex items-center gap-2 px-4 py-2 rounded-full"
        [class]="statusBgClass()">
        <mat-icon class="!text-xl" [style.color]="statusColor()">{{ statusIcon() }}</mat-icon>
        <div>
          <span class="block text-xs text-text-subtle font-medium">Status IA</span>
          <span class="block text-sm font-bold" [style.color]="statusColor()">{{ statusLabel() }}</span>
        </div>
      </div>
    </div>
  `
})
export class PatientInfoBarComponent {
  session = input<SessionOut | null>(null);

  patientName = computed(() => {
    const s = this.session();
    if (!s) return 'Carregando...';
    // patient_code is the identifier, use it to derive a display name
    return s.patient_code || 'Paciente';
  });

  clinicalDetails = computed(() => {
    const s = this.session();
    if (!s) return '';
    // Usa as notas da sessão como detalhes clínicos, se houver
    return s.notes || 'Dados clínicos não informados';
  });

  sala = computed(() => {
    const s = this.session();
    return s ? "A" + s.id : "--";
  });
  leito = computed(() => "--");

  startTime = computed(() => {
    const s = this.session();
    if (!s) return '--:--';
    const d = new Date(s.created_at);
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  });

  elapsedTime = computed(() => {
    const s = this.session();
    if (!s) return "";
    const start = new Date(s.created_at).getTime();
    const now = Date.now();
    const diffMs = now - start;
    const hours = Math.floor(diffMs / 3600000);
    const minutes = Math.floor((diffMs % 3600000) / 60000);
    return "ha " + hours.toString().padStart(2, "0") + "h" + minutes.toString().padStart(2, "0");
  });

  statusColor = computed(() => {
    const level = this.session()?.ira_level;
    switch (level) {
      case 'critico': return '#EF4444';
      case 'moderado': return '#F59E0B';
      default: return '#10B981';
    }
  });

  statusIcon = computed(() => {
    const level = this.session()?.ira_level;
    switch (level) {
      case 'critico': return 'error';
      case 'moderado': return 'warning';
      default: return 'check_circle';
    }
  });

  statusLabel = computed(() => {
    const level = this.session()?.ira_level;
    switch (level) {
      case 'critico': return 'Risco Crítico';
      case 'moderado': return 'Risco Moderado';
      default: return 'Baixo risco';
    }
  });

  statusBgClass = computed(() => {
    const level = this.session()?.ira_level;
    switch (level) {
      case 'critico': return 'bg-danger-500/10 border border-danger-500/30';
      case 'moderado': return 'bg-warning/10 border border-warning/30';
      default: return 'bg-success/10 border border-success/30';
    }
  });
}
