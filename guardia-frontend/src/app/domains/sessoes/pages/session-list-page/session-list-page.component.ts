import { Component, inject, OnInit, signal, Inject } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { SessionsService } from '../../services/sessions.service';
import { SessionOut } from '../../models/sessions.models';
import { SessionEditDialogComponent } from '../../components/session-edit-dialog.component';

@Component({
  selector: 'app-session-list-page',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatIconModule, MatButtonModule, MatPaginatorModule, MatSnackBarModule, MatDialogModule, RouterLink],
  providers: [DatePipe],
  template: `
    <div class="p-8 max-w-[1400px] mx-auto min-h-screen flex flex-col gap-6">
      
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 class="text-3xl font-bold text-white mb-1 flex items-center gap-3">
            <mat-icon class="text-primary-500 text-3xl">folder_shared</mat-icon>
            Sessões Clínicas
          </h1>
          <p class="text-text-muted">Gerencie os prontuários, análises e mídias dos atendimentos.</p>
        </div>
        
        <a mat-flat-button color="primary" routerLink="/sessoes/nova">
          <mat-icon>add</mat-icon> Nova Sessão
        </a>
      </div>

      <div class="glass-card flex-1 flex flex-col overflow-hidden animate-slide-up">
        
        <div class="flex-1 overflow-auto">
          @if (loading()) {
            <div class="flex justify-center items-center h-48">
              <mat-icon class="animate-spin text-primary-500 text-4xl">autorenew</mat-icon>
            </div>
          } @else if (sessions().length === 0) {
            <div class="flex flex-col items-center justify-center h-48 text-text-muted">
              <mat-icon class="text-4xl mb-2 opacity-50">inbox</mat-icon>
              <p>Nenhuma sessão clínica encontrada.</p>
            </div>
          } @else {
            <table mat-table [dataSource]="sessions()" class="w-full bg-transparent">
              
              <ng-container matColumnDef="title">
                <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs"> Título / Código </th>
                <td mat-cell *matCellDef="let s" class="border-b border-border/50 py-3">
                  <div class="font-bold text-white">{{ s.title }}</div>
                  <div class="text-xs text-text-muted font-mono bg-bg/50 inline-block px-1.5 rounded mt-1">{{ s.patient_code }}</div>
                </td>
              </ng-container>

              <ng-container matColumnDef="status">
                <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs"> Status </th>
                <td mat-cell *matCellDef="let s" class="border-b border-border/50">
                  <span class="status-chip" [ngClass]="'status-chip--' + s.status">
                    <span class="dot"></span>
                    {{ getStatusLabel(s.status) }}
                  </span>
                </td>
              </ng-container>

              <ng-container matColumnDef="ira">
                <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs"> IGA </th>
                <td mat-cell *matCellDef="let s" class="border-b border-border/50">
                  @if (s.iga_score !== null) {
                    <span class="iga-badge" [ngClass]="'iga-badge--' + s.iga_level">
                      {{ s.iga_score | number:'1.1-1' }}
                    </span>
                  } @else {
                    <span class="text-text-subtle text-sm">-</span>
                  }
                </td>
              </ng-container>

              <ng-container matColumnDef="date">
                <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs"> Data </th>
                <td mat-cell *matCellDef="let s" class="border-b border-border/50 text-sm text-text-muted">
                  {{ s.created_at | date:'dd/MM/yyyy HH:mm' }}
                </td>
              </ng-container>

              <ng-container matColumnDef="actions">
                <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs text-right"> Ações </th>
                <td mat-cell *matCellDef="let s" class="border-b border-border/50 text-right whitespace-nowrap">
                  <button mat-icon-button color="primary" (click)="editSession(s)" title="Editar">
                    <mat-icon>edit</mat-icon>
                  </button>
                  <button mat-icon-button color="warn" (click)="deleteSession(s)" title="Excluir">
                    <mat-icon>delete</mat-icon>
                  </button>
                  <a mat-icon-button color="primary" [routerLink]="['/sessoes', s.id]" title="Ver Detalhes">
                    <mat-icon>visibility</mat-icon>
                  </a>
                  <a mat-icon-button class="text-secondary-400" [routerLink]="['/analise/multimodal', s.id]" title="Resumo da IA">
                    <mat-icon>psychology</mat-icon>
                  </a>
                </td>
              </ng-container>

              <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
              <tr mat-row *matRowDef="let row; columns: displayedColumns;" class="hover:bg-surface2/50 transition-colors"></tr>
            </table>
          }
        </div>
        
        <mat-paginator 
          class="border-t border-border bg-transparent text-white"
          [length]="totalElements()"
          [pageSize]="pageSize()"
          [pageSizeOptions]="[10, 20, 50]"
          (page)="onPageChange($event)">
        </mat-paginator>

      </div>
    </div>
  `
})
export class SessionListPageComponent implements OnInit {
  private readonly sessionsService = inject(SessionsService);
  private readonly snackBar = inject(MatSnackBar);
  private readonly dialog = inject(MatDialog);

  displayedColumns = ['title', 'status', 'ira', 'date', 'actions'];
  
  sessions = signal<SessionOut[]>([]);
  loading = signal(true);
  totalElements = signal(0);
  pageSize = signal(20);
  pageIndex = signal(0);

  ngOnInit() {
    this.loadSessions();
  }

  loadSessions() {
    this.loading.set(true);
    const skip = this.pageIndex() * this.pageSize();
    
    this.sessionsService.getSessions(skip, this.pageSize()).subscribe({
      next: (res) => {
        this.sessions.set(res.items);
        this.totalElements.set(res.total);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      }
    });
  }

  onPageChange(event: PageEvent) {
    this.pageIndex.set(event.pageIndex);
    this.pageSize.set(event.pageSize);
    this.loadSessions();
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      pending: 'Pendente',
      processing: 'Processando IA',
      completed: 'Concluído',
      error: 'Erro'
    };
    return labels[status] || status;
  }

  editSession(session: SessionOut) {
    const dialogRef = this.dialog.open(SessionEditDialogComponent, {
      width: '500px',
      data: { session }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.sessionsService.updateSession(session.id, result).subscribe({
          next: () => {
            this.snackBar.open('Sessão atualizada com sucesso!', 'OK', { duration: 3000 });
            this.loadSessions();
          },
          error: () => {
            this.snackBar.open('Erro ao atualizar a sessão.', 'Fechar', { duration: 3000 });
          }
        });
      }
    });
  }

  deleteSession(session: SessionOut) {
    const dialogRef = this.dialog.open(SessionDeleteDialogComponent, {
      width: '400px',
      data: { session }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.sessionsService.deleteSession(session.id).subscribe({
          next: () => {
            this.snackBar.open('Sessão excluída com sucesso!', 'OK', { duration: 3000 });
            this.loadSessions();
          },
          error: () => {
            this.snackBar.open('Erro ao excluir a sessão.', 'Fechar', { duration: 3000 });
          }
        });
      }
    });
  }
}

@Component({
  selector: 'app-session-delete-dialog',
  standalone: true,
  imports: [MatButtonModule, MatDialogModule],
  template: `
    <h2 mat-dialog-title class="text-white">Confirmar Exclusão</h2>
    <mat-dialog-content class="text-text-muted mt-2">
      Tem certeza que deseja excluir a sessão <strong class="text-white">{{ data.session.title || 'Sem título' }}</strong>?<br><br>
      Esta ação não pode ser desfeita.
    </mat-dialog-content>
    <mat-dialog-actions align="end" class="mb-2">
      <button mat-button mat-dialog-close>Cancelar</button>
      <button mat-flat-button color="warn" [mat-dialog-close]="true">Excluir</button>
    </mat-dialog-actions>
  `
})
export class SessionDeleteDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: { session: SessionOut }) {}
}
