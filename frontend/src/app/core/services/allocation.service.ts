import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';

import { Allocation } from '../models/allocation.model';

export interface AllocationSaveItem {
  category_id: string;
  allocated_amount: number;
}

@Injectable({ providedIn: 'root' })
export class AllocationService {
  private readonly allocations$ = new BehaviorSubject<Allocation[]>([]);
  readonly currentAllocations$ = this.allocations$.asObservable();

  constructor(private http: HttpClient) {}

  loadCurrent(): Observable<Allocation[]> {
    return this.http
      .get<Allocation[]>('/api/v1/plans/current/allocations')
      .pipe(tap((allocations) => this.allocations$.next(allocations)));
  }

  save(items: AllocationSaveItem[]): Observable<Allocation[]> {
    return this.http
      .put<Allocation[]>('/api/v1/plans/current/allocations', { allocations: items })
      .pipe(tap((allocations) => this.allocations$.next(allocations)));
  }

  quickLog(categoryId: string, amount: number): Observable<Allocation> {
    return this.http.post<Allocation>('/api/v1/plans/current/allocations/quick-log', {
      category_id: categoryId,
      amount,
    });
  }
}
