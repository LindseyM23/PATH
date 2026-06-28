import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, catchError, of } from 'rxjs';

import { Reflection } from '../models/reflection.model';

@Injectable({ providedIn: 'root' })
export class ReflectionService {
  constructor(private http: HttpClient) {}

  loadPrevious(): Observable<Reflection | null> {
    return this.http.get<Reflection>('/api/v1/plans/previous/reflection').pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 404) {
          return of(null);
        }
        throw error;
      }),
    );
  }
}
