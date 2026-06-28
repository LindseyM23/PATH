import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, catchError, of, tap } from 'rxjs';

import { MonthlyPlan } from '../models/monthly-plan.model';

@Injectable({ providedIn: 'root' })
export class PlanService {
  private readonly currentPlan$ = new BehaviorSubject<MonthlyPlan | null>(null);
  readonly plan$ = this.currentPlan$.asObservable();

  constructor(private http: HttpClient) {}

  fetchCurrent(): Observable<MonthlyPlan | null> {
    return this.http.get<MonthlyPlan>('/api/v1/plans/current').pipe(
      tap((plan) => this.currentPlan$.next(plan)),
      catchError((error: HttpErrorResponse) => {
        if (error.status === 404) {
          this.currentPlan$.next(null);
          return of(null);
        }
        throw error;
      }),
    );
  }

  saveSalary(amount: number): Observable<MonthlyPlan> {
    return this.http
      .put<MonthlyPlan>('/api/v1/plans/current', { salary_amount: amount })
      .pipe(tap((plan) => this.currentPlan$.next(plan)));
  }
}
