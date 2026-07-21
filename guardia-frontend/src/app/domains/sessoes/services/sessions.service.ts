import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { PaginatedSessions, SessionOut, SessionStatus } from '../models/sessions.models';

export interface DashboardMetricsOut {
  total_sessions: number;
  critical_alerts: number;
  average_ira: number;
  monthly_distribution: { label: string; value: number }[];
}

@Injectable({ providedIn: 'root' })
export class SessionsService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/sessions`;

  getSessions(skip = 0, limit = 20, status?: SessionStatus): Observable<PaginatedSessions> {
    let params = new HttpParams().set('skip', skip).set('limit', limit);
    if (status) {
      params = params.set('status', status);
    }
    return this.http.get<PaginatedSessions>(this.baseUrl, { params });
  }

  getSession(id: number): Observable<SessionOut> {
    return this.http.get<SessionOut>(`${this.baseUrl}/${id}`);
  }

  createSession(data: { title: string; patient_code: string; notes?: string }): Observable<{ session: SessionOut; message: string }> {
    return this.http.post<{ session: SessionOut; message: string }>(this.baseUrl, data);
  }

  updateSession(id: number, data: { title?: string; notes?: string; status?: string }): Observable<SessionOut> {
    return this.http.patch<SessionOut>(`${this.baseUrl}/${id}`, data);
  }

  uploadMedia(sessionId: number, file: File, mediaType: 'video' | 'audio' | 'document'): Observable<any> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    formData.append('media_type', mediaType);
    
    // O Angular HttpClient define o boundary do multipart/form-data automaticamente quando enviamos FormData
    return this.http.post(`${this.baseUrl}/${sessionId}/media`, formData);
  }

  getDashboardMetrics(): Observable<DashboardMetricsOut> {
    return this.http.get<DashboardMetricsOut>(`${this.baseUrl}/metrics/dashboard`);
  }

  downloadSessionReportPdf(sessionId: number): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/${sessionId}/report/pdf`, { responseType: 'blob' });
  }

  deleteSession(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  deleteMediaFile(mediaId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/media/${mediaId}`);
  }
}
