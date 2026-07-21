import { Component, inject, OnInit, OnDestroy, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subject, timer, switchMap, takeUntil, catchError, of } from 'rxjs';

import { AlertsService } from '../../services/alerts.service';
import { AlertOut } from '../../models/alerts.models';
import { AlertFiltersComponent, AlertFilterValues } from '../../components/alert-filters.component';

@Component({
  selector: 'app-alerts-center-page',
  standalone: true,
  imports: [
    CommonModule, 
    MatIconModule, 
    MatButtonModule, 
    MatProgressSpinnerModule,
    AlertFiltersComponent
  ],
  template: `
    <div class="p-8 max-w-[1200px] mx-auto min-h-screen flex flex-col gap-6">
      
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 class="text-3xl font-bold text-white mb-1 flex items-center gap-3">
            Alertas
          </h1>
          <p class="text-text-muted">Indicadores que necessitam avaliação humana</p>
        </div>
        
        <div class="flex items-center gap-2 text-sm text-text-subtle bg-surface2/50 px-3 py-1.5 rounded-full border border-border">
          <div class="w-2 h-2 rounded-full bg-success animate-pulse"></div>
          Sincronizado
        </div>
      </div>

      <!-- Filters -->
      <app-alert-filters 
        [filters]="currentFilters()" 
        [counts]="alertCounts()"
        (filtersChange)="onFiltersChanged($event)">
      </app-alert-filters>

      <!-- Content -->
      <div class="flex-1 flex flex-col relative animate-slide-up">
        
        <!-- Loading Overlay -->
        @if (loading() && alerts().length === 0) {
          <div class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-bg/80 backdrop-blur-sm">
            <mat-spinner diameter="40"></mat-spinner>
          </div>
        }

        <!-- Empty State -->
        @if (!loading() && alerts().length === 0) {
          <div class="flex flex-col items-center justify-center h-64 text-center opacity-70 m-auto">
            <div class="w-20 h-20 rounded-full bg-surface2 flex items-center justify-center mb-4">
              <mat-icon class="text-5xl text-success">verified</mat-icon>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Nenhum Alerta</h3>
            <p class="text-text-subtle max-w-sm">Os filtros aplicados não retornaram resultados ou sua operação está totalmente segura no momento.</p>
          </div>
        }
        
        <!-- List -->
        <div class="flex flex-col gap-8">
          
          <!-- Alertas Críticos -->
          @if (criticalAlerts().length > 0) {
            <div>
              <h2 class="text-danger-500 font-bold mb-4">Alertas críticos</h2>
              <div class="flex flex-col gap-3">
                @for (alert of criticalAlerts(); track alert.id) {
                  <div class="bg-danger-500/5 border border-danger-500/20 rounded-xl p-5 hover:bg-danger-500/10 transition-colors cursor-pointer flex items-start gap-4">
                    <mat-icon class="text-danger-500 mt-1 !text-[28px] !w-[28px] !h-[28px]">error</mat-icon>
                    <div class="flex-1">
                      <div class="flex justify-between items-start mb-1">
                        <h3 class="text-danger-400 font-bold text-base m-0">{{ alert.title }}</h3>
                        <span class="text-xs text-text-muted font-mono">{{ alert.created_at | date:'HH:mm' }}</span>
                      </div>
                      <p class="text-white text-sm mb-3">{{ alert.description }}</p>
                      <div class="flex items-center justify-between">
                        <p class="text-xs text-text-muted">Paciente: {{ alert.patient_code || '---' }} • {{ alert.session_title || 'Sessão ' + alert.session_id }}</p>
                        <div class="flex items-center gap-3">
                          <span class="bg-danger-500/20 text-danger-400 text-xs font-bold px-2 py-0.5 rounded border border-danger-500/30">Crítico</span>
                          <button mat-button class="!text-text-muted hover:!text-white hover:!bg-surface" (click)="dismiss(alert.id)" [disabled]="isAcknowledging() === alert.id">
                            <mat-icon>visibility_off</mat-icon> Ignorar
                          </button>
                          <button mat-button class="!text-danger-400 hover:!bg-danger-500/10" (click)="acknowledge(alert.id)" [disabled]="isAcknowledging() === alert.id">
                            <mat-icon>check</mat-icon> Reconhecer
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                }
              </div>
              <div class="mt-3 text-right">
                <a class="text-xs text-primary-400 font-semibold hover:underline cursor-pointer">Ver todos os críticos ({{ criticalAlerts().length }}) →</a>
              </div>
            </div>
          }

          <!-- Alertas de Atenção -->
          @if (moderateAlerts().length > 0) {
            <div>
              <h2 class="text-warning font-bold mb-4">Alertas de atenção</h2>
              <div class="flex flex-col gap-3">
                @for (alert of moderateAlerts(); track alert.id) {
                  <div class="bg-warning/5 border border-warning/20 rounded-xl p-5 hover:bg-warning/10 transition-colors cursor-pointer flex items-start gap-4">
                    <mat-icon class="text-warning mt-1 !text-[28px] !w-[28px] !h-[28px]">warning</mat-icon>
                    <div class="flex-1">
                      <div class="flex justify-between items-start mb-1">
                        <h3 class="text-warning-500 font-bold text-base m-0">{{ alert.title }}</h3>
                        <span class="text-xs text-text-muted font-mono">{{ alert.created_at | date:'HH:mm' }}</span>
                      </div>
                      <p class="text-white text-sm mb-3">{{ alert.description }}</p>
                      <div class="flex items-center justify-between">
                        <p class="text-xs text-text-muted">Paciente: {{ alert.patient_code || '---' }} • {{ alert.session_title || 'Sessão ' + alert.session_id }}</p>
                        <div class="flex items-center gap-3">
                          <span class="bg-warning/20 text-warning-400 text-xs font-bold px-2 py-0.5 rounded border border-warning/30">Atenção</span>
                          <button mat-button class="!text-text-muted hover:!text-white hover:!bg-surface" (click)="dismiss(alert.id)" [disabled]="isAcknowledging() === alert.id">
                            <mat-icon>visibility_off</mat-icon> Ignorar
                          </button>
                          <button mat-button class="!text-warning-500 hover:!bg-warning/10" (click)="acknowledge(alert.id)" [disabled]="isAcknowledging() === alert.id">
                            <mat-icon>check</mat-icon> Reconhecer
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                }
              </div>
              <div class="mt-3 text-right">
                <a class="text-xs text-primary-400 font-semibold hover:underline cursor-pointer">Ver todos os de atenção ({{ moderateAlerts().length }}) →</a>
              </div>
            </div>
          }



        </div>
      </div>
    </div>
  `
})
export class AlertsCenterPageComponent implements OnInit, OnDestroy {
  private readonly alertsService = inject(AlertsService);
  private readonly snackBar = inject(MatSnackBar);
  private readonly destroy$ = new Subject<void>();
  private readonly refreshTrigger$ = new Subject<void>();

  loading = signal(true);
  isAcknowledging = signal<number | null>(null);
  alerts = signal<AlertOut[]>([]);
  
  currentFilters = signal<AlertFilterValues>({
    severity: 'all',
    unacknowledgedOnly: true // Default to showing only actionable items
  });

  alertCounts = computed(() => {
    const all = this.alerts();
    return {
      all: all.length,
      critical: all.filter(a => a.severity === 'critical').length,
      moderate: all.filter(a => a.severity === 'moderate').length,
      informative: 0
    };
  });

  // Computed signals for categorized alerts
  criticalAlerts = computed(() => {
    const filter = this.currentFilters().severity;
    if (filter !== 'all' && filter !== 'critical') return [];
    return this.alerts().filter(a => a.severity === 'critical');
  });
  
  moderateAlerts = computed(() => {
    const filter = this.currentFilters().severity;
    if (filter !== 'all' && filter !== 'moderate') return [];
    return this.alerts().filter(a => a.severity === 'moderate');
  });

  ngOnInit() {
    // Polling de 10 segundos
    timer(0, 10000).pipe(
      takeUntil(this.destroy$),
      switchMap(() => {
        const filters = this.currentFilters();
        return this.alertsService.getAlerts(0, 50, undefined, filters.unacknowledgedOnly).pipe(
          catchError(() => {
            console.error('Failed to poll alerts');
            return of({ items: [], total: 0 });
          })
        );
      })
    ).subscribe((res: any) => {
      this.alerts.set(res.items);
      this.loading.set(false);
    });

    // Gatilho manual para recarregar imediatamente ao mudar filtros
    this.refreshTrigger$.pipe(
      takeUntil(this.destroy$),
      switchMap(() => {
        this.loading.set(true);
        const filters = this.currentFilters();
        return this.alertsService.getAlerts(0, 50, undefined, filters.unacknowledgedOnly).pipe(
          catchError(() => of({ items: [], total: 0 }))
        );
      })
    ).subscribe((res: any) => {
      this.alerts.set(res.items);
      this.loading.set(false);
    });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onFiltersChanged(newFilters: AlertFilterValues) {
    this.currentFilters.set(newFilters);
    this.refreshTrigger$.next(); // Force refresh outside of polling cycle
  }

  acknowledge(id: number) {
    this.isAcknowledging.set(id);
    this.alertsService.acknowledgeAlert(id).subscribe({
      next: () => {
        this.snackBar.open('Alerta marcado como reconhecido.', 'OK', { duration: 3000 });
        this.isAcknowledging.set(null);
        this.refreshTrigger$.next(); // Recarrega a lista
      },
      error: () => {
        this.snackBar.open('Erro ao reconhecer alerta.', 'Fechar', { duration: 3000 });
        this.isAcknowledging.set(null);
      }
    });
  }

  dismiss(id: number) {
    this.isAcknowledging.set(id); // Reusa o mesmo loading signal para travar botões
    this.alertsService.dismissAlert(id).subscribe({
      next: () => {
        this.snackBar.open('Alerta ignorado com sucesso.', 'OK', { duration: 3000 });
        this.isAcknowledging.set(null);
        this.refreshTrigger$.next();
      },
      error: () => {
        this.snackBar.open('Erro ao ignorar alerta.', 'Fechar', { duration: 3000 });
        this.isAcknowledging.set(null);
      }
    });
  }

}
