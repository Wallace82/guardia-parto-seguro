import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar } from '@angular/material/snack-bar';
import { SessionsService } from '../../services/sessions.service';

@Component({
  selector: 'app-session-create-page',
  standalone: true,
  imports: [
    CommonModule, 
    ReactiveFormsModule, 
    RouterLink, 
    MatIconModule, 
    MatButtonModule, 
    MatFormFieldModule, 
    MatInputModule
  ],
  template: `
    <div class="p-8 max-w-[800px] mx-auto min-h-screen">
      
      <div class="flex items-center gap-2 mb-8 animate-fade-in">
        <a mat-icon-button color="primary" routerLink="/sessoes">
          <mat-icon>arrow_back</mat-icon>
        </a>
        <h1 class="text-3xl font-bold text-white m-0">Nova Sessão</h1>
      </div>

      <div class="glass-card p-8 animate-slide-up">
        <form [formGroup]="form" (ngSubmit)="onSubmit()" class="flex flex-col gap-4">
          
          <div class="bg-primary-500/10 border border-primary-500/30 p-4 rounded-lg flex gap-3 text-primary-200 text-sm mb-4">
            <mat-icon class="text-primary-400 shrink-0">privacy_tip</mat-icon>
            <p><strong>LGPD:</strong> Ao preencher o "Código do Paciente", utilize um identificador anonimizado. Não insira CPF, nome completo ou dados pessoais que identifiquem diretamente o paciente.</p>
          </div>

          <mat-form-field appearance="outline" class="w-full">
            <mat-label>Título da Sessão</mat-label>
            <input matInput formControlName="title" placeholder="Ex: Consulta Pré-natal - Semana 36">
            <mat-error *ngIf="form.get('title')?.hasError('required')">Título é obrigatório.</mat-error>
          </mat-form-field>

          <mat-form-field appearance="outline" class="w-full">
            <mat-label>Código do Paciente (Anonimizado)</mat-label>
            <input matInput formControlName="patient_code" placeholder="Ex: PAC-2024-001">
            <mat-error *ngIf="form.get('patient_code')?.hasError('required')">Código do paciente é obrigatório.</mat-error>
          </mat-form-field>

          <mat-form-field appearance="outline" class="w-full">
            <mat-label>Notas Clínicas (Opcional)</mat-label>
            <textarea matInput formControlName="notes" rows="4" placeholder="Observações prévias relevantes para a IA..."></textarea>
          </mat-form-field>

          <div class="flex justify-end gap-4 mt-4">
            <a mat-button routerLink="/sessoes">Cancelar</a>
            <button mat-flat-button color="primary" type="submit" [disabled]="form.invalid || loading()">
              @if (loading()) {
                <mat-icon class="animate-spin">autorenew</mat-icon>
              }
              Criar Sessão e Adicionar Mídia
            </button>
          </div>
        </form>
      </div>
    </div>
  `
})
export class SessionCreatePageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly sessionsService = inject(SessionsService);
  private readonly router = inject(Router);
  private readonly snackBar = inject(MatSnackBar);

  loading = signal(false);

  form = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(3)]],
    patient_code: ['', [Validators.required, Validators.minLength(3)]],
    notes: ['']
  });

  onSubmit() {
    if (this.form.invalid) return;

    this.loading.set(true);
    const data = this.form.getRawValue() as any;

    this.sessionsService.createSession(data).subscribe({
      next: (res) => {
        this.snackBar.open('Sessão criada com sucesso!', 'OK', { duration: 3000 });
        this.router.navigate(['/sessoes', res.session.id]);
      },
      error: (err) => {
        console.error(err);
        this.snackBar.open('Erro ao criar sessão.', 'Fechar', { duration: 3000 });
        this.loading.set(false);
      }
    });
  }
}
