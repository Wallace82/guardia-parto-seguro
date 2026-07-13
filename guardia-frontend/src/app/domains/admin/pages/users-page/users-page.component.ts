import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../../../domains/auth/services/auth.service';
import { UserProfile } from '../../../../domains/auth/models/auth.models';

@Component({
  selector: 'app-admin-users-page',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatIconModule, MatButtonModule, MatChipsModule],
  template: `
    <div class="p-8 max-w-[1200px] mx-auto min-h-screen flex flex-col gap-6">
      
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 class="text-3xl font-bold text-white mb-1 flex items-center gap-3">
            <mat-icon class="text-primary-500 text-3xl">admin_panel_settings</mat-icon>
            Gestão de Usuários
          </h1>
          <p class="text-text-muted">Área restrita. Gerencie o acesso dos profissionais ao GuardIA.</p>
        </div>
        
        <button mat-flat-button color="primary">
          <mat-icon>person_add</mat-icon> Novo Usuário
        </button>
      </div>

      <div class="glass-card flex-1 overflow-hidden animate-slide-up">
        <table mat-table [dataSource]="users()" class="w-full bg-transparent">
          
          <ng-container matColumnDef="name">
            <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs"> Nome </th>
            <td mat-cell *matCellDef="let user" class="border-b border-border/50 py-3">
              <div class="font-bold text-white">{{ user.full_name }}</div>
              <div class="text-xs text-text-muted">{{ user.email }}</div>
            </td>
          </ng-container>

          <ng-container matColumnDef="role">
            <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs"> Cargo/Perfil </th>
            <td mat-cell *matCellDef="let user" class="border-b border-border/50">
              <span class="px-2 py-1 rounded text-xs font-bold uppercase tracking-wider"
                    [ngClass]="{
                      'bg-danger-500/20 text-danger-400': user.role === 'admin',
                      'bg-warning-500/20 text-warning-400': user.role === 'gestor',
                      'bg-primary-500/20 text-primary-400': user.role === 'profissional'
                    }">
                {{ user.role }}
              </span>
            </td>
          </ng-container>

          <ng-container matColumnDef="status">
            <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs"> Status </th>
            <td mat-cell *matCellDef="let user" class="border-b border-border/50">
              <mat-chip [color]="user.is_active ? 'primary' : 'warn'" highlighted>
                {{ user.is_active ? 'Ativo' : 'Inativo' }}
              </mat-chip>
            </td>
          </ng-container>

          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef class="text-text-muted uppercase text-xs text-right"> Ações </th>
            <td mat-cell *matCellDef="let user" class="border-b border-border/50 text-right">
              <button mat-icon-button color="primary"><mat-icon>edit</mat-icon></button>
              <button mat-icon-button color="warn" [disabled]="user.role === 'admin'"><mat-icon>block</mat-icon></button>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns;" class="hover:bg-surface2/50 transition-colors"></tr>
        </table>
      </div>
    </div>
  `
})
export class AdminUsersPageComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly snackBar = inject(MatSnackBar);

  displayedColumns = ['name', 'role', 'status', 'actions'];
  users = signal<UserProfile[]>([]);

  ngOnInit() {
    this.authService.listUsers().subscribe({
      next: (data) => {
        this.users.set(data);
      },
      error: () => {
        this.snackBar.open('Erro ao carregar lista de usuários.', 'Fechar', { duration: 3000 });
      }
    });
  }
}
