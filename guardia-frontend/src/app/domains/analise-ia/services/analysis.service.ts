import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { SessionAnalysisOut } from '../models/analysis.models';

@Injectable({ providedIn: 'root' })
export class AnalysisService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/sessions`;

  getAnalysis(sessionId: number): Observable<SessionAnalysisOut> {
    return this.http.get<SessionAnalysisOut>(`${this.baseUrl}/${sessionId}/analysis`);
  }
}
