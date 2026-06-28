import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, map, tap } from 'rxjs';

import { AuthResponse, User } from '../models/user.model';

const TOKEN_KEY = 'path.access_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly currentUser$ = new BehaviorSubject<User | null>(null);
  readonly user$ = this.currentUser$.asObservable();
  readonly isAuthenticated$ = this.user$.pipe(map((user) => !!user));

  constructor(private http: HttpClient) {}

  register(email: string, password: string, displayName?: string): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>('/api/v1/auth/register', {
        email,
        password,
        display_name: displayName,
      })
      .pipe(tap((response) => this.applyAuthResponse(response)));
  }

  login(email: string, password: string): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>('/api/v1/auth/login', { email, password })
      .pipe(tap((response) => this.applyAuthResponse(response)));
  }

  restoreSession(): Observable<User | null> {
    const token = this.getToken();
    if (!token) {
      return new BehaviorSubject<User | null>(null).asObservable();
    }
    return this.http.get<User>('/api/v1/auth/me').pipe(
      tap((user) => this.currentUser$.next(user)),
    );
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    this.currentUser$.next(null);
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  private applyAuthResponse(response: AuthResponse): void {
    localStorage.setItem(TOKEN_KEY, response.access_token);
    this.currentUser$.next(response.user);
  }
}
