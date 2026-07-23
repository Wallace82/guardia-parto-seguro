import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { AuthStore } from '../../domains/auth/store/auth.store';

interface MenuItem {
  icon: string;
  label: string;
  route: string;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, MatIconModule],
  template: `
    <aside class="w-64 h-screen bg-bg border-r border-border flex flex-col fixed left-0 top-0 z-30">
      <!-- Logo -->
      <div class="h-16 flex items-center px-5 border-b border-border gap-2">
        <div class="w-8 h-8 rounded-lg bg-primary-500/20 flex items-center justify-center">
          <mat-icon class="text-primary-400 !text-lg">shield</mat-icon>
        </div>
        <div class="flex flex-col leading-none">
          <span class="text-base font-bold text-white tracking-wide">Guard<span class="text-primary-400">IA</span></span>
          <span class="text-[10px] text-text-subtle font-medium tracking-wider uppercase">Parto Seguro</span>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 py-4 px-3 flex flex-col gap-1 overflow-y-auto">
        @for (item of mainMenuItems; track item.route) {
          <a [routerLink]="item.route"
            routerLinkActive="active-link"
            [routerLinkActiveOptions]="{exact: item.route === '/dashboard'}"
            class="sidebar-link">
            <mat-icon>{{ item.icon }}</mat-icon>
            <span class="font-medium">{{ item.label }}</span>
          </a>
        }

        @if (authStore.userRole() === 'admin' || authStore.userRole() === 'gestor') {
          <div class="mt-6 mb-2 px-4 text-[10px] font-bold text-text-subtle uppercase tracking-[0.15em]">Administração</div>

          @for (item of adminMenuItems; track item.route) {
            <a [routerLink]="item.route"
              routerLinkActive="active-link"
              class="sidebar-link">
              <mat-icon>{{ item.icon }}</mat-icon>
              <span class="font-medium">{{ item.label }}</span>
            </a>
          }
        }
      </nav>

      <!-- Logout -->
      <div class="p-3 border-t border-border">
        <button (click)="authStore.logout()" class="sidebar-link w-full !text-text-muted hover:!text-danger-400 hover:!bg-danger-500/10">
          <mat-icon>logout</mat-icon>
          <span class="font-medium">Sair</span>
        </button>
      </div>
    </aside>
  `,
  styles: [`
    .sidebar-link {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.625rem 1rem;
      border-radius: 0.5rem;
      color: #94A3B8;
      font-size: 0.875rem;
      transition: all 0.2s ease;
      cursor: pointer;
      border: none;
      background: transparent;
      text-decoration: none;
      position: relative;
      text-align: left;

      &:hover {
        color: white;
        background: #1E293B;
      }

      &.active-link {
        color: white;
        background: rgba(139, 92, 246, 0.12);

        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 4px;
          bottom: 4px;
          width: 3px;
          background: #8B5CF6;
          border-radius: 0 3px 3px 0;
        }

        mat-icon {
          color: #a78bfa;
        }
      }
    }
  `]
})
export class SidebarComponent {
  public readonly authStore = inject(AuthStore);

  mainMenuItems: MenuItem[] = [
    { icon: 'home', label: 'Início', route: '/dashboard' },
    { icon: 'people', label: 'Sessões', route: '/sessoes' },
    { icon: 'summarize', label: 'Relatórios', route: '/relatorios' },
    { icon: 'notification_important', label: 'Alertas', route: '/alertas' },
  ];

  adminMenuItems: MenuItem[] = [
    { icon: 'policy', label: 'Auditoria', route: '/admin/auditoria' },
    { icon: 'settings', label: 'Configurações', route: '/admin/configuracoes' },
  ];
}
