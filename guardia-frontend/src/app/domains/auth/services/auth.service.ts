import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { StorageService } from '../../../core/services/storage.service';
import {
  AuthTokens,
  ChangePasswordRequest,
  CreateUserRequest,
  CreateUserResponse,
  LoginCredentials,
  LogoutRequest,
  RefreshTokenRequest,
  UserProfile,
} from '../models/auth.models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly storage = inject(StorageService);
  private readonly baseUrl = `${environment.apiUrl}/auth`;

  login(credentials: LoginCredentials): Observable<AuthTokens> {
    return this.http.post<AuthTokens>(`${this.baseUrl}/login`, credentials).pipe(
      tap((tokens) => {
        this.storage.setAccessToken(tokens.access_token);
        this.storage.setRefreshToken(tokens.refresh_token);
      }),
    );
  }

  getMe(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.baseUrl}/me`).pipe(
      tap((user) => this.storage.setUser(user)),
    );
  }

  refreshToken(): Observable<AuthTokens> {
    const refresh_token = this.storage.getRefreshToken();
    if (!refresh_token) {
      throw new Error('No refresh token available');
    }
    const req: RefreshTokenRequest = { refresh_token };
    
    return this.http.post<AuthTokens>(`${this.baseUrl}/refresh`, req).pipe(
      tap((tokens) => {
        this.storage.setAccessToken(tokens.access_token);
        this.storage.setRefreshToken(tokens.refresh_token);
      }),
    );
  }

  logout(): Observable<void> {
    const refresh_token = this.storage.getRefreshToken();
    const req: LogoutRequest = { refresh_token: refresh_token || '' };
    
    return this.http.post<void>(`${this.baseUrl}/logout`, req).pipe(
      tap(() => this.storage.clearAll()),
    );
  }

  changePassword(data: ChangePasswordRequest): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/password/change`, data);
  }

  createUser(data: CreateUserRequest): Observable<CreateUserResponse> {
    return this.http.post<CreateUserResponse>(`${this.baseUrl}/users`, data);
  }

  listUsers(): Observable<UserProfile[]> {
    return this.http.get<UserProfile[]>(`${this.baseUrl}/users`);
  }
}
