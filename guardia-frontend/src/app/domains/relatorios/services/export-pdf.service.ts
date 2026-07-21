import { Injectable, inject } from '@angular/core';
import { SessionsService } from '../../sessoes/services/sessions.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

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

  async exportElementToPdf(elementId: string, filename: string) {
    const element = document.getElementById(elementId);
    if (!element) {
      this.snackBar.open('Elemento do relatório não encontrado.', 'Fechar', { duration: 3000 });
      return;
    }

    this.snackBar.open('Gerando PDF visual do relatório...', 'Aguarde', { duration: 3000 });

    try {
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff' // Fundo branco para impressão
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save(filename);
      
      this.snackBar.open('PDF exportado com sucesso!', 'OK', { duration: 3000 });
    } catch (error) {
      console.error('Erro ao exportar PDF:', error);
      this.snackBar.open('Erro ao gerar PDF visual.', 'Fechar', { duration: 3000 });
    }
  }
}
