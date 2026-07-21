import { Component, EventEmitter, Input, Output, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDialog, MatDialogModule, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-media-uploader',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule, MatProgressBarModule, MatDialogModule],
  template: `
    <div class="border-2 border-dashed border-border rounded-xl p-8 flex flex-col items-center justify-center text-center transition-colors"
         [ngClass]="{
           'border-primary-500 bg-primary-500/5': isDragging,
           'bg-surface2/30 hover:bg-surface2/50 hover:border-primary-500/50': !isDragging
         }"
         (dragover)="onDragOver($event)"
         (dragleave)="onDragLeave($event)"
         (drop)="onDrop($event)">
      
      @if (uploading()) {
        <div class="w-full max-w-md flex flex-col items-center">
          <mat-icon class="text-4xl text-primary-500 mb-4 animate-bounce">cloud_upload</mat-icon>
          <h3 class="text-white font-bold mb-2">Enviando Arquivo...</h3>
          <p class="text-sm text-text-muted mb-4">{{ selectedFile?.name }}</p>
          <mat-progress-bar mode="indeterminate" color="primary" class="w-full rounded-full"></mat-progress-bar>
          <p class="text-xs text-text-subtle mt-2">Isso pode levar alguns minutos dependendo do tamanho do vídeo.</p>
        </div>
      } @else {
        <div class="w-20 h-20 rounded-full bg-surface flex items-center justify-center text-text-muted mb-4">
          <mat-icon class="text-4xl">upload_file</mat-icon>
        </div>
        <h3 class="text-xl font-bold text-white mb-2">Envie arquivos para a IA</h3>
        <p class="text-text-muted mb-6 max-w-md">Arraste e solte vídeos, áudios ou documentos (PDF, imagens) do atendimento para iniciar o processamento inteligente.</p>
        
        <div class="flex gap-4">
          <input type="file" #fileInput class="hidden" (change)="onFileSelected($event)" accept="video/*,audio/*,application/pdf,image/*,.mp4,.mp3,.wav,.m4a,.mkv,.avi,.ogg">
          <button mat-flat-button color="primary" (click)="fileInput.click()">
            <mat-icon>add_circle</mat-icon> Selecionar Arquivo
          </button>
        </div>
        
        <div class="mt-6 flex gap-4 text-xs text-text-subtle">
          <span class="flex items-center gap-1"><mat-icon class="text-[14px] w-[14px] h-[14px]">videocam</mat-icon> Vídeo (Max 2GB)</span>
          <span class="flex items-center gap-1"><mat-icon class="text-[14px] w-[14px] h-[14px]">mic</mat-icon> Áudio (Max 500MB)</span>
          <span class="flex items-center gap-1"><mat-icon class="text-[14px] w-[14px] h-[14px]">description</mat-icon> Doc (Max 50MB)</span>
        </div>
      }
    </div>
  `
})
export class MediaUploaderComponent {
  @Input() uploading = signal(false);
  @Output() fileDropped = new EventEmitter<{ file: File; type: 'video' | 'audio' | 'document' }>();

  private dialog = inject(MatDialog);

  isDragging = false;
  selectedFile: File | null = null;

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
    
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      this.handleFile(event.dataTransfer.files[0]);
    }
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.handleFile(input.files[0]);
    }
  }

  private handleFile(file: File) {
    this.selectedFile = file;
    let type: 'video' | 'audio' | 'document' = 'document';
    
    if (file.type.startsWith('video/')) type = 'video';
    else if (file.type.startsWith('audio/')) type = 'audio';
    
    // Workaround para gravações de voz que celulares salvam como .mp4
    if (type === 'video' && file.name.toLowerCase().endsWith('.mp4')) {
      const dialogRef = this.dialog.open(AudioVideoDialogComponent, {
        width: '450px',
        panelClass: 'bg-surface' // Mantém o fundo escuro do modal se houver tema
      });

      dialogRef.afterClosed().subscribe((result: 'audio' | 'video' | undefined) => {
        if (result) {
          type = result;
          this.fileDropped.emit({ file, type });
        } else {
          // Usuário cancelou ou fechou no X sem selecionar
          this.selectedFile = null;
        }
      });
      return;
    }
    
    this.fileDropped.emit({ file, type });
  }
}

@Component({
  selector: 'app-audio-video-dialog',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  template: `
    <div class="p-6 bg-surface border border-border rounded-xl text-white">
      <div class="flex items-center gap-3 mb-4 text-warning">
        <mat-icon class="text-3xl text-primary-500">help_outline</mat-icon>
        <h2 class="text-xl font-bold m-0 text-white">Confirmar tipo de mídia</h2>
      </div>
      <p class="text-text-muted mb-6 leading-relaxed">
        Detectamos um arquivo MP4. Em alguns celulares, gravações de voz são salvas neste formato. <br><br>
        O que exatamente você está enviando?
      </p>
      <div class="flex justify-end gap-3">
        <button mat-stroked-button (click)="dialogRef.close('video')" class="!text-text-muted hover:!bg-surface2 !border-border">
          <mat-icon>videocam</mat-icon> Vídeo
        </button>
        <button mat-flat-button color="primary" (click)="dialogRef.close('audio')">
          <mat-icon>mic</mat-icon> Apenas Áudio (Voz)
        </button>
      </div>
    </div>
  `,
  styles: [`
    :host { display: block; }
  `]
})
export class AudioVideoDialogComponent {
  constructor(public dialogRef: MatDialogRef<AudioVideoDialogComponent>) {}
}
