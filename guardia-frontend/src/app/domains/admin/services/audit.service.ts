import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface AuditLog {
  id: string;
  action: string;
  resource: string;
  user: string;
  role: string;
  created_at: string;
}

export interface PaginatedAuditLogs {
  total: number;
  items: AuditLog[];
}

@Injectable({ providedIn: 'root' })
export class AuditService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/audit/logs`;

  getLogs(skip = 0, limit = 50, search = ''): Observable<PaginatedAuditLogs> {
    let params = new HttpParams().set('skip', skip).set('limit', limit);
    if (search) {
      params = params.set('search', search);
    }
    return this.http.get<PaginatedAuditLogs>(this.baseUrl, { params });
  }
}
