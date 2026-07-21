import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { SessionOut } from '../models/sessions.models';

@Component({
  selector: 'app-session-edit-dialog',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatDialogModule,
    MatFormFieldModule, MatInputModule, MatButtonModule
  ],
  template: `
    <h2 mat-dialog-title class="text-white">Editar Paciente / Atendimento</h2>
    
    <mat-dialog-content>
      <form [formGroup]="editForm" class="flex flex-col gap-4 mt-2">
        <mat-form-field appearance="outline" class="w-full">
          <mat-label>Título / Nome Simbólico</mat-label>
          <input matInput formControlName="title" placeholder="Ex: Acompanhamento Pré-natal">
          @if (editForm.get('title')?.hasError('required')) {
            <mat-error>O título é obrigatório</mat-error>
          }
        </mat-form-field>
        
        <mat-form-field appearance="outline" class="w-full">
          <mat-label>Código do Paciente</mat-label>
          <input matInput [value]="data.session.patient_code" disabled>
          <mat-hint>O código do paciente não pode ser alterado por segurança.</mat-hint>
        </mat-form-field>

        <mat-form-field appearance="outline" class="w-full">
          <mat-label>Anotações (Opcional)</mat-label>
          <textarea matInput formControlName="notes" rows="4" placeholder="Observações clínicas..."></textarea>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancelar</button>
      <button mat-flat-button color="primary" (click)="save()" [disabled]="editForm.invalid">Salvar</button>
    </mat-dialog-actions>
  `
})
export class SessionEditDialogComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  readonly dialogRef = inject(MatDialogRef<SessionEditDialogComponent>);
  readonly data: { session: SessionOut } = inject(MAT_DIALOG_DATA);

  editForm!: FormGroup;

  ngOnInit() {
    this.editForm = this.fb.group({
      title: [this.data.session.title, [Validators.required, Validators.minLength(3)]],
      notes: [this.data.session.notes || '']
    });
  }

  save() {
    if (this.editForm.valid) {
      this.dialogRef.close(this.editForm.value);
    }
  }
}
