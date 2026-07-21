import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { AlertOut, AlertSeverity, PaginatedAlerts } from '../models/alerts.models';

@Injectable({ providedIn: 'root' })
export class AlertsService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/alerts`;

  getAlerts(
    skip = 0,
    limit = 50,
    severity?: AlertSeverity,
    unacknowledgedOnly = false
  ): Observable<PaginatedAlerts> {
    let params = new HttpParams()
      .set('skip', skip)
      .set('limit', limit)
      .set('unacknowledged_only', unacknowledgedOnly);
      
    if (severity) {
      params = params.set('severity', severity);
    }
    
    return this.http.get<PaginatedAlerts>(this.baseUrl, { params });
  }

  acknowledgeAlert(id: number): Observable<AlertOut> {
    return this.http.patch<AlertOut>(`${this.baseUrl}/${id}/acknowledge`, {});
  }

  dismissAlert(id: number): Observable<AlertOut> {
    return this.http.patch<AlertOut>(`${this.baseUrl}/${id}/dismiss`, {});
  }
}
