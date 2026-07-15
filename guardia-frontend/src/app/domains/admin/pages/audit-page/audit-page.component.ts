import { Component, signal, OnInit, inject, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatPaginatorModule, MatPaginator, PageEvent } from '@angular/material/paginator';
import { MatMenuModule } from '@angular/material/menu';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { AuditService, AuditLog, PaginatedAuditLogs } from '../../services/audit.service';

@Component({
  selector: 'app-admin-audit-page',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatIconModule, MatButtonModule, MatChipsModule, MatPaginatorModule, ReactiveFormsModule, MatMenuModule],
  template: `
    <div class="p-8 max-w-[1200px] mx-auto min-h-screen flex flex-col gap-6">
      
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 class="text-3xl font-bold text-white mb-1 flex items-center gap-3">
            <mat-icon class="text-primary-500 text-3xl">policy</mat-icon>
            Auditoria de Sistema
          </h1>
          <p class="text-text-muted">Área restrita. Acompanhe os registros de ações e modificações no GuardIA.</p>
        </div>
        
        <div class="flex gap-3">
          <button mat-stroked-button class="!border-border !text-white">
            <mat-icon>download</mat-icon> Exportar CSV
          </button>
          <button mat-flat-button color="primary">
            <mat-icon>refresh</mat-icon> Atualizar
          </button>
        </div>
      </div>

      <!-- Filters (Mock) -->
      <div class="bg-surface2/30 border border-border rounded-xl p-4 flex gap-4 animate-fade-in">
        <div class="flex-1 relative">
          <mat-icon class="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">search</mat-icon>
          <input type="text" [formControl]="searchControl" placeholder="Buscar por recurso, usuário ou ação..." 
                 class="w-full bg-surface border border-border rounded-lg py-2 pl-10 pr-4 text-white focus:outline-none focus:border-primary-500 transition-colors">
        </div>
        <button mat-stroked-button class="!border-border !text-white" [matMenuTriggerFor]="filterMenu">
          <mat-icon>filter_list</mat-icon> Filtros
        </button>
        
        <mat-menu #filterMenu="matMenu" class="!bg-surface border border-border">
          <div class="px-4 py-2 text-xs font-bold text-text-muted uppercase tracking-wider">Filtrar por Ação</div>
          <button mat-menu-item (click)="setFilter('CREATE_SESSION')" class="!text-white hover:!bg-surface2">Criação de Sessão</button>
          <button mat-menu-item (click)="setFilter('USER_LOGIN')" class="!text-white hover:!bg-surface2">Logins de Usuários</button>
          <button mat-menu-item (click)="setFilter('UPDATE_CONFIG')" class="!text-white hover:!bg-surface2">Mudança de Configuração</button>
          <button mat-menu-item (click)="setFilter('UPDATE_ALERT')" class="!text-white hover:!bg-surface2">Atualização de Alerta</button>
          <button mat-menu-item (click)="setFilter('DELETE_MEDIA')" class="!text-white hover:!bg-surface2">Mídias Deletadas</button>
          <div class="h-px bg-border my-1"></div>
          <button mat-menu-item (click)="setFilter('')" class="!text-primary-400 hover:!bg-surface2">
            <mat-icon class="!text-primary-400">clear_all</mat-icon> Limpar Filtros
          </button>
        </mat-menu>
      </div>

      <!-- Table -->
      <div class="glass-card flex-1 overflow-hidden animate-slide-up flex flex-col">
        <table mat-table [dataSource]="logs()" class="w-full bg-transparent flex-1">
          
          <ng-container matColumnDef="timestamp">
            <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs w-48"> Data / Hora </th>
            <td mat-cell *matCellDef="let log" class="border-b border-border/50 py-3 text-text-muted font-mono text-sm">
              {{ log.created_at }}
            </td>
          </ng-container>

          <ng-container matColumnDef="user">
            <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs"> Usuário </th>
            <td mat-cell *matCellDef="let log" class="border-b border-border/50 py-3">
              <div class="font-bold text-white">{{ log.user }}</div>
              <div class="text-xs text-text-muted capitalize">{{ log.role }}</div>
            </td>
          </ng-container>

          <ng-container matColumnDef="action">
            <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs"> Ação </th>
            <td mat-cell *matCellDef="let log" class="border-b border-border/50">
              <span class="px-2 py-1 rounded text-xs font-bold tracking-wider bg-surface2 text-white border border-border">
                {{ log.action }}
              </span>
            </td>
          </ng-container>

          <ng-container matColumnDef="resource">
            <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs"> Recurso Afetado </th>
            <td mat-cell *matCellDef="let log" class="border-b border-border/50 text-white font-mono text-sm">
              {{ log.resource }}
            </td>
          </ng-container>

          <ng-container matColumnDef="details">
            <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs text-right"> Detalhes </th>
            <td mat-cell *matCellDef="let log" class="border-b border-border/50 text-right">
              <button mat-icon-button class="!text-primary-400 hover:!bg-primary-500/10"><mat-icon>visibility</mat-icon></button>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns;" class="hover:bg-surface2/50 transition-colors"></tr>
        </table>
        
        <!-- Paginator Real -->
        <mat-paginator [length]="totalLogs()"
                       [pageSize]="pageSize()"
                       [pageSizeOptions]="[10, 25, 50, 100]"
                       (page)="onPageChange($event)"
                       class="bg-transparent border-t border-border text-text-muted">
        </mat-paginator>
      </div>
    </div>
  `
})
export class AdminAuditPageComponent implements OnInit {
  private readonly auditService = inject(AuditService);
  private readonly snackBar = inject(MatSnackBar);

  displayedColumns = ['timestamp', 'user', 'action', 'resource', 'details'];
  logs = signal<AuditLog[]>([]);
  totalLogs = signal<number>(0);
  isLoading = signal(true);
  pageSize = signal(10);
  pageIndex = signal(0);
  
  searchControl = new FormControl('');

  ngOnInit() {
    this.loadLogs();
    
    this.searchControl.valueChanges.pipe(
      debounceTime(500),
      distinctUntilChanged()
    ).subscribe(() => {
      this.pageIndex.set(0);
      this.loadLogs();
    });
  }

  loadLogs() {
    this.isLoading.set(true);
    const skip = this.pageIndex() * this.pageSize();
    const search = this.searchControl.value || '';
    
    this.auditService.getLogs(skip, this.pageSize(), search).subscribe({
      next: (data: PaginatedAuditLogs) => {
        this.logs.set(data.items);
        this.totalLogs.set(data.total);
        this.isLoading.set(false);
      },
      error: () => {
        this.snackBar.open('Erro ao carregar logs de auditoria', 'Fechar', { duration: 3000 });
        this.isLoading.set(false);
      }
    });
  }
  
  onPageChange(event: PageEvent) {
    this.pageSize.set(event.pageSize);
    this.pageIndex.set(event.pageIndex);
    this.loadLogs();
  }

  setFilter(action: string) {
    this.searchControl.setValue(action);
  }
}
