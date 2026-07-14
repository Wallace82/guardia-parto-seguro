import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';

export interface ConfirmDialogData {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDestructive?: boolean;
}

@Component({
  selector: 'app-confirm-dialog',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatDialogModule, MatIconModule],
  template: `
    <div class="glass-card !border-none !rounded-none">
      <h2 mat-dialog-title class="!text-white flex items-center gap-2 m-0 p-6 pb-2">
        <mat-icon [class.text-danger-500]="data.isDestructive" [class.text-primary-400]="!data.isDestructive">
          {{ data.isDestructive ? 'warning' : 'help_outline' }}
        </mat-icon>
        {{ data.title }}
      </h2>
      
      <mat-dialog-content class="!text-text-muted px-6 pb-6 pt-2">
        <p>{{ data.message }}</p>
      </mat-dialog-content>
      
      <mat-dialog-actions class="px-6 py-4 border-t border-border flex justify-end gap-2 bg-surface2/30">
        <button mat-button mat-dialog-close class="text-text-muted hover:text-white transition-colors">
          {{ data.cancelText || 'Cancelar' }}
        </button>
        <button mat-flat-button [color]="data.isDestructive ? 'warn' : 'primary'" [mat-dialog-close]="true">
          {{ data.confirmText || 'Confirmar' }}
        </button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      background-color: var(--color-surface);
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--color-border);
    }
    
    .glass-card {
      background: rgba(30, 41, 59, 0.6);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }
  `]
})
export class ConfirmDialogComponent {
  data = inject<ConfirmDialogData>(MAT_DIALOG_DATA);
}
