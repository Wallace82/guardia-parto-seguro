import { Injectable, inject } from '@angular/core';
import { SessionsService } from '../../sessoes/services/sessions.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({ providedIn: 'root' })
export class ExportPdfService {
  private readonly sessionsService = inject(SessionsService);
  private readonly snackBar = inject(MatSnackBar);
  
  exportDashboardReport() {
    this.snackBar.open('Relatório gerencial em desenvolvimento (via Python).', 'OK', { duration: 3000 });
  }

  exportSessionReport(sessionId: number) {
    this.snackBar.open('Gerando prontuário (PDF) no backend...', 'Aguarde', { duration: 2000 });
    
    this.sessionsService.downloadSessionReportPdf(sessionId).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Prontuario_GuardIA_Sessao_${sessionId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: () => {
        this.snackBar.open('Erro ao baixar relatório PDF.', 'Fechar', { duration: 3000 });
      }
    });
  }
}
