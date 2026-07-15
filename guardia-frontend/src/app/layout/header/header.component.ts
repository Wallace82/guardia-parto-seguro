import { Component, inject } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { AuthStore } from '../../domains/auth/store/auth.store';

import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { ProfileDialogComponent } from './profile-dialog.component';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule, MatDialogModule, MatIconModule, MatMenuModule, MatButtonModule, MatDividerModule],
  template: `
    <header class="h-16 bg-surface/80 backdrop-blur-md border-b border-border flex items-center justify-between px-6 sticky top-0 z-20 w-full">
      <!-- Title Area (Left) -->
      <div>
        <h2 class="text-lg font-semibold text-white"></h2>
      </div>

      <!-- Actions Area (Right) -->
      <div class="flex items-center gap-4">
        
        <!-- Notifications -->
        <button mat-icon-button routerLink="/alertas" class="text-text-muted relative hover:text-white transition-colors">
          <mat-icon>notifications</mat-icon>
          <span class="absolute top-1 right-1 w-2.5 h-2.5 bg-danger-500 rounded-full border-2 border-surface"></span>
        </button>

        <!-- User Profile Dropdown -->
        <button mat-button [matMenuTriggerFor]="userMenu" class="!px-2 !rounded-full">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center border border-primary-500/30">
              <span class="font-bold text-sm">{{ getInitials() }}</span>
            </div>
            <div class="hidden md:flex flex-col items-start leading-none text-left">
              <span class="text-sm font-medium text-white">{{ authStore.userName() || 'Usuário' }}</span>
              <span class="text-xs text-text-muted capitalize">{{ authStore.userRole() || 'Perfil' }}</span>
            </div>
            <mat-icon class="text-text-muted text-sm w-4 h-4">expand_more</mat-icon>
          </div>
        </button>

        <mat-menu #userMenu="matMenu" xPosition="before" class="bg-surface2 border border-border mt-2">
          <div class="px-4 py-3 border-b border-border md:hidden">
            <div class="text-sm font-medium text-white">{{ authStore.userName() }}</div>
            <div class="text-xs text-text-muted capitalize">{{ authStore.userRole() }}</div>
          </div>
          <button mat-menu-item (click)="openProfile()">
            <mat-icon class="text-text-muted">person</mat-icon>
            <span class="text-white">Meu Perfil</span>
          </button>
          <button mat-menu-item routerLink="/admin/configuracoes" *ngIf="authStore.userRole() === 'admin' || authStore.userRole() === 'gestor'">
            <mat-icon class="text-text-muted">settings</mat-icon>
            <span class="text-white">Preferências</span>
          </button>
          <mat-divider class="!border-border"></mat-divider>
          <button mat-menu-item (click)="authStore.logout()" class="hover:bg-danger-500/10">
            <mat-icon class="text-danger-400">logout</mat-icon>
            <span class="text-danger-400">Sair do Sistema</span>
          </button>
        </mat-menu>

      </div>
    </header>
  `
})
export class HeaderComponent {
  public readonly authStore = inject(AuthStore);
  private readonly dialog = inject(MatDialog);

  getInitials(): string {
    const name = this.authStore.userName();
    if (!name) return 'U';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  openProfile() {
    this.dialog.open(ProfileDialogComponent, {
      width: '400px',
      panelClass: 'custom-dialog-container'
    });
  }
}
