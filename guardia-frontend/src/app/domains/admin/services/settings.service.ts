import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface SystemSettings {
  email_alerts: boolean;
  push_notifications: boolean;
  strict_mode: boolean;
  auto_process_audio: boolean;
  retention_days: number;
  timeout_minutes: number;
}

@Injectable({ providedIn: 'root' })
export class SettingsService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/settings`;

  getSettings(): Observable<SystemSettings> {
    return this.http.get<SystemSettings>(this.baseUrl);
  }

  updateSettings(settings: SystemSettings): Observable<SystemSettings> {
    return this.http.put<SystemSettings>(this.baseUrl, settings);
  }
}
