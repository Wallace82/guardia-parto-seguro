import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';

@Component({
  selector: 'app-notes-analysis-dialog',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule, MatDialogModule],
  template: `
    <div class="p-6 bg-surface border border-accent-500/30 shadow-glow-accent rounded-lg max-w-2xl w-full mx-auto text-white">
      <h3 class="text-xl font-bold text-accent-400 flex items-center gap-2 mb-4 uppercase tracking-wider">
        <mat-icon>auto_awesome</mat-icon> Avaliação Textual da IA
      </h3>
      
      <div class="text-sm text-white/90 whitespace-pre-line leading-relaxed max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
        {{ data?.text || 'Nenhuma análise disponível.' }}
      </div>
      
      <div class="mt-6 flex justify-end">
        <button mat-flat-button color="primary" (click)="close()">Fechar</button>
      </div>
    </div>
  `,
  styles: [`
    .custom-scrollbar::-webkit-scrollbar {
      width: 6px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
      background-color: rgba(255, 255, 255, 0.2);
      border-radius: 4px;
    }
  `]
})
export class NotesAnalysisDialogComponent {
  data = inject(MAT_DIALOG_DATA);
  dialogRef = inject(MatDialogRef<NotesAnalysisDialogComponent>);

  close() {
    this.dialogRef.close();
  }
}
