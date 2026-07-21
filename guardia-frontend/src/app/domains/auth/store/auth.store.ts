import { inject } from '@angular/core';
import { Router } from '@angular/router';
import {
  signalStore,
  withState,
  withMethods,
  withComputed,
  patchState,
} from '@ngrx/signals';
import { computed } from '@angular/core';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { pipe, switchMap, tap, catchError, of, finalize } from 'rxjs';
import { tapResponse } from '@ngrx/operators';
import { AuthService } from '../services/auth.service';
import { StorageService } from '../../../core/services/storage.service';
import { LoginCredentials, UserProfile, UserRole } from '../models/auth.models';
import { HttpErrorResponse } from '@angular/common/http';

type AuthState = {
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
};

const initialState: AuthState = {
  user: null,
  loading: false,
  error: null,
};

export const AuthStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withComputed(({ user }) => ({
    isAuthenticated: computed(() => !!user()),
    userRole: computed(() => (user()?.role as UserRole) ?? null),
    userName: computed(() => user()?.full_name ?? ''),
  })),
  withMethods(
    (
      store,
      authService = inject(AuthService),
      storage = inject(StorageService),
      router = inject(Router),
    ) => ({
      // Load user from storage on init
      loadUserFromStorage() {
        const user = storage.getUser<UserProfile>();
        if (user) {
          patchState(store, { user });
        }
      },

      // RxMethod for login
      login: rxMethod<LoginCredentials>(
        pipe(
          tap(() => patchState(store, { loading: true, error: null })),
          switchMap((credentials) =>
            authService.login(credentials).pipe(
              switchMap(() => authService.getMe()),
              tapResponse({
                next: (user: UserProfile) => {
                  patchState(store, { user, loading: false });
                  router.navigate(['/dashboard']);
                },
                error: (error: HttpErrorResponse) => {
                  let errorMessage = 'Falha ao autenticar.';
                  if (error.status === 401) {
                    errorMessage = 'Email ou senha incorretos.';
                  } else if (error.error?.detail) {
                    errorMessage = String(error.error.detail);
                  }
                  patchState(store, { error: errorMessage, loading: false });
                },
              }),
            ),
          ),
        ),
      ),

      // Logout method
      logout: rxMethod<void>(
        pipe(
          tap(() => patchState(store, { loading: true })),
          switchMap(() =>
            authService.logout().pipe(
              catchError(() => {
                // If API logout fails, still clear local state
                storage.clearAll();
                return of(null);
              }),
              finalize(() => {
                patchState(store, { user: null, loading: false });
                storage.clearAll();
                router.navigate(['/auth/login']);
              }),
            ),
          ),
        ),
      ),
    }),
  ),
);
