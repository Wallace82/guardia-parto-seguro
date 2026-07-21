import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthStore } from '../../domains/auth/store/auth.store';
import { AuthService } from '../../domains/auth/services/auth.service';

@Component({
  selector: 'app-profile-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatIconModule, ReactiveFormsModule],
  template: `
    <div class="bg-surface2 text-white overflow-hidden rounded-xl">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-border flex justify-between items-center bg-surface/50">
        <h2 class="text-xl font-bold m-0 flex items-center gap-2">
          <mat-icon class="text-primary-400">person</mat-icon>
          Meu Perfil
        </h2>
        <button mat-icon-button mat-dialog-close class="text-text-muted hover:text-white">
          <mat-icon>close</mat-icon>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 flex flex-col gap-6">
        
        <!-- User Info -->
        <div class="flex items-center gap-4 bg-surface p-4 rounded-lg border border-border">
          <div class="w-12 h-12 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center border border-primary-500/30 text-xl font-bold">
            {{ getInitials() }}
          </div>
          <div>
            <h3 class="text-lg font-bold m-0">{{ authStore.userName() }}</h3>
            <p class="text-sm text-text-muted m-0">{{ authStore.user()?.email || 'email@guardia.com' }}</p>
            <span class="inline-block mt-1 px-2 py-0.5 rounded text-xs font-bold bg-primary-500/20 text-primary-400 border border-primary-500/30 capitalize">
              {{ authStore.userRole() }}
            </span>
          </div>
        </div>

        <hr class="border-border">

        <!-- Change Password Form -->
        <div>
          <h3 class="text-md font-bold mb-4 flex items-center gap-2">
            <mat-icon class="text-text-muted text-sm">lock</mat-icon>
            Trocar Senha
          </h3>
          
          <form [formGroup]="passwordForm" (ngSubmit)="changePassword()" class="flex flex-col gap-4">
            
            <div class="flex flex-col gap-1">
              <label class="text-xs font-medium text-text-muted uppercase tracking-wider">Senha Atual</label>
              <input type="password" formControlName="current_password"
                     class="w-full bg-surface border border-border rounded-lg py-2 px-3 text-white focus:outline-none focus:border-primary-500 transition-colors"
                     placeholder="Sua senha atual">
            </div>

            <div class="flex flex-col gap-1">
              <label class="text-xs font-medium text-text-muted uppercase tracking-wider">Nova Senha</label>
              <input type="password" formControlName="new_password"
                     class="w-full bg-surface border border-border rounded-lg py-2 px-3 text-white focus:outline-none focus:border-primary-500 transition-colors"
                     placeholder="Sua nova senha">
            </div>

            <div class="flex justify-end mt-2">
              <button mat-flat-button color="primary" type="submit" [disabled]="passwordForm.invalid || isChanging()">
                <mat-icon *ngIf="isChanging()"><span class="animate-spin material-icons">autorenew</span></mat-icon>
                <mat-icon *ngIf="!isChanging()">save</mat-icon>
                Salvar Nova Senha
              </button>
            </div>
          </form>
        </div>

      </div>
    </div>
  `
})
export class ProfileDialogComponent {
  public readonly authStore = inject(AuthStore);
  private readonly authService = inject(AuthService);
  private readonly fb = inject(FormBuilder);
  private readonly snackBar = inject(MatSnackBar);
  private readonly dialogRef = inject(MatDialogRef<ProfileDialogComponent>);

  isChanging = signal(false);

  passwordForm = this.fb.group({
    current_password: ['', Validators.required],
    new_password: ['', [Validators.required, Validators.minLength(6)]]
  });

  getInitials(): string {
    const name = this.authStore.userName();
    if (!name) return 'U';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  changePassword() {
    if (this.passwordForm.invalid) return;

    this.isChanging.set(true);
    const { current_password, new_password } = this.passwordForm.value;

    this.authService.changePassword({ current_password: current_password!, new_password: new_password! }).subscribe({
      next: () => {
        this.isChanging.set(false);
        this.snackBar.open('Senha alterada com sucesso!', 'OK', { duration: 3000, panelClass: ['success-snackbar'] });
        this.passwordForm.reset();
        this.dialogRef.close();
      },
      error: (err) => {
        this.isChanging.set(false);
        const msg = err.error?.detail || 'Erro ao alterar a senha. Verifique sua senha atual.';
        this.snackBar.open(msg, 'Fechar', { duration: 4000 });
      }
    });
  }
}
