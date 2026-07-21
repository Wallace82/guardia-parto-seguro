import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { AuthStore } from '../../store/auth.store';

@Component({
  selector: 'app-login-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
  ],
  template: `
    <div class="login-form-container glass-card p-8 w-full max-w-md mx-auto relative overflow-hidden">
      <!-- Glow background effect -->
      <div class="absolute -top-16 -right-16 w-32 h-32 bg-primary-500 rounded-full blur-3xl opacity-20"></div>
      <div class="absolute -bottom-16 -left-16 w-32 h-32 bg-secondary-500 rounded-full blur-3xl opacity-20"></div>

      <div class="relative z-10 flex flex-col items-center mb-8">
        <mat-icon class="text-primary-400 text-5xl w-12 h-12 mb-2">medical_services</mat-icon>
        <h1 class="text-3xl font-bold text-white mb-1">GuardIA</h1>
        <p class="text-text-muted text-sm uppercase tracking-widest font-semibold">Parto Seguro</p>
      </div>

      @if (authStore.error()) {
        <div class="bg-danger/10 border border-danger/30 text-danger-500 px-4 py-3 rounded-md mb-6 text-sm flex items-start gap-2 animate-fade-in">
          <mat-icon class="text-sm w-4 h-4 mt-0.5">error_outline</mat-icon>
          <span>{{ authStore.error() }}</span>
        </div>
      }

      <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="flex flex-col gap-4 relative z-10">
        
        <mat-form-field appearance="outline" class="w-full">
          <mat-label>Email</mat-label>
          <input matInput type="email" formControlName="email" placeholder="medico@hospital.com" autocomplete="email">
          <mat-icon matPrefix class="mr-2 text-text-muted">person</mat-icon>
          @if (loginForm.controls['email'].hasError('required') && loginForm.controls['email'].touched) {
            <mat-error>Email é obrigatório</mat-error>
          }
          @if (loginForm.controls['email'].hasError('email') && loginForm.controls['email'].touched) {
            <mat-error>E-mail inválido</mat-error>
          }
        </mat-form-field>

        <mat-form-field appearance="outline" class="w-full">
          <mat-label>Senha</mat-label>
          <input matInput [type]="hidePassword ? 'password' : 'text'" formControlName="password" autocomplete="current-password">
          <mat-icon matPrefix class="mr-2 text-text-muted">lock</mat-icon>
          <button mat-icon-button matSuffix (click)="hidePassword = !hidePassword" type="button" [attr.aria-label]="'Ocultar senha'" [attr.aria-pressed]="hidePassword">
            <mat-icon class="text-text-muted">{{hidePassword ? 'visibility_off' : 'visibility'}}</mat-icon>
          </button>
          @if (loginForm.controls['password'].hasError('required') && loginForm.controls['password'].touched) {
            <mat-error>Senha é obrigatória</mat-error>
          }
          @if (loginForm.controls['password'].hasError('minlength') && loginForm.controls['password'].touched) {
            <mat-error>Mínimo de 8 caracteres</mat-error>
          }
        </mat-form-field>

        <button mat-raised-button color="primary" type="submit" class="w-full h-12 mt-2 text-lg" [disabled]="loginForm.invalid || authStore.loading()">
          @if (authStore.loading()) {
            <span class="flex items-center gap-2">
              <mat-icon class="animate-spin">autorenew</mat-icon> Autenticando...
            </span>
          } @else {
            Entrar no Sistema
          }
        </button>

      </form>
    </div>
  `,
  styles: [`
    /* Sobrescritas locais se necessário, a maioria vem do styles.scss */
    .mat-mdc-form-field-icon-prefix {
      display: flex;
      align-items: center;
      justify-content: center;
    }
  `]
})
export class LoginFormComponent {
  private readonly fb = inject(FormBuilder);
  public readonly authStore = inject(AuthStore);

  hidePassword = true;

  loginForm = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]]
  });

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.authStore.login(this.loginForm.getRawValue());
    } else {
      this.loginForm.markAllAsTouched();
    }
  }
}
