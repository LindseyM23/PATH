import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';

import { Category } from '../models/category.model';

@Injectable({ providedIn: 'root' })
export class CategoryService {
  private readonly categories$ = new BehaviorSubject<Category[]>([]);
  readonly allCategories$ = this.categories$.asObservable();

  constructor(private http: HttpClient) {}

  loadCategories(): Observable<Category[]> {
    return this.http
      .get<Category[]>('/api/v1/categories')
      .pipe(tap((categories) => this.categories$.next(categories)));
  }
}
