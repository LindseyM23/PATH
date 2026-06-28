import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';

import { Goal } from '../models/goal.model';

@Injectable({ providedIn: 'root' })
export class GoalService {
  private readonly goals$ = new BehaviorSubject<Goal[]>([]);
  readonly currentGoals$ = this.goals$.asObservable();

  constructor(private http: HttpClient) {}

  loadGoals(): Observable<Goal[]> {
    return this.http
      .get<Goal[]>('/api/v1/goals')
      .pipe(tap((goals) => this.goals$.next(goals)));
  }

  create(name: string, targetAmount: number, icon?: string): Observable<Goal> {
    return this.http
      .post<Goal>('/api/v1/goals', { name, target_amount: targetAmount, icon })
      .pipe(tap((goal) => this.goals$.next([...this.goals$.value, goal])));
  }

  contribute(goalId: string, amount: number): Observable<Goal> {
    return this.http.post<Goal>(`/api/v1/goals/${goalId}/contribute`, { amount }).pipe(
      tap((updated) => {
        this.goals$.next(this.goals$.value.map((g) => (g.id === updated.id ? updated : g)));
      }),
    );
  }

  remove(goalId: string): Observable<void> {
    return this.http.delete<void>(`/api/v1/goals/${goalId}`).pipe(
      tap(() => {
        this.goals$.next(this.goals$.value.filter((g) => g.id !== goalId));
      }),
    );
  }
}
