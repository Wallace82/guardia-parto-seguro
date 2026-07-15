import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { AlertSeverity } from '../models/alerts.models';

export interface AlertFilterValues {
  severity: AlertSeverity | 'all';
  unacknowledgedOnly: boolean;
}

@Component({
  selector: 'app-alert-filters',
  standalone: true,
  imports: [CommonModule, FormsModule, MatFormFieldModule, MatSelectModule, MatSlideToggleModule, MatButtonModule, MatIconModule],
  template: `
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      
      <!-- Tabs -->
      <div class="flex flex-wrap gap-2">
        <button 
          (click)="selectTab('all')"
          class="flex items-center gap-2 px-6 py-3 rounded-t-lg font-semibold transition-all border-b-2"
          [class]="activeTab === 'all' ? 'bg-primary-500/10 text-primary-400 border-primary-500' : 'text-text-muted border-transparent hover:bg-surface2'">
          Todos
          <span class="text-lg font-bold" [class.text-primary-400]="activeTab === 'all'">{{ counts.all }}</span>
        </button>

        <button 
          (click)="selectTab('critical')"
          class="flex items-center gap-2 px-6 py-3 rounded-t-lg font-semibold transition-all border-b-2"
          [class]="activeTab === 'critical' ? 'bg-danger-500/10 text-danger-500 border-danger-500' : 'text-text-muted border-transparent hover:bg-surface2'">
          Críticos
          <span class="text-lg font-bold" [class.text-danger-500]="activeTab === 'critical'">{{ counts.critical }}</span>
        </button>

        <button 
          (click)="selectTab('moderate')"
          class="flex items-center gap-2 px-6 py-3 rounded-t-lg font-semibold transition-all border-b-2"
          [class]="activeTab === 'moderate' ? 'bg-warning/10 text-warning border-warning' : 'text-text-muted border-transparent hover:bg-surface2'">
          Atenção
          <span class="text-lg font-bold" [class.text-warning]="activeTab === 'moderate'">{{ counts.moderate }}</span>
        </button>

        <button 
          (click)="selectTab('informative')"
          class="flex items-center gap-2 px-6 py-3 rounded-t-lg font-semibold transition-all border-b-2"
          [class]="activeTab === 'informative' ? 'bg-primary-500/10 text-primary-400 border-primary-500' : 'text-text-muted border-transparent hover:bg-surface2'">
          Informativos
          <span class="text-lg font-bold" [class.text-primary-400]="activeTab === 'informative'">{{ counts.informative }}</span>
        </button>
      </div>

      <!-- Filters button -->
      <button mat-stroked-button class="!rounded-lg !py-1">
        <mat-icon>filter_alt</mat-icon> Filtros
      </button>

    </div>
  `
})
export class AlertFiltersComponent implements OnInit {
  @Input() filters: AlertFilterValues = { severity: 'all', unacknowledgedOnly: true };
  @Input() counts = { all: 0, critical: 0, moderate: 0, informative: 0 };
  @Output() filtersChange = new EventEmitter<AlertFilterValues>();

  activeTab: 'all' | 'critical' | 'moderate' | 'informative' = 'all';

  ngOnInit() {
    this.activeTab = (this.filters.severity as any) || 'all';
  }

  selectTab(tab: 'all' | 'critical' | 'moderate' | 'informative') {
    this.activeTab = tab;
    // We map 'informative' to 'all' for the backend, but we'll handle it on the frontend
    const severity = tab === 'informative' ? 'all' : tab;
    
    this.filters = {
      ...this.filters,
      severity: severity as any
    };
    this.filtersChange.emit(this.filters);
  }
}
