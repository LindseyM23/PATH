import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'path.theme';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly theme$ = new BehaviorSubject<Theme | null>(this.readStoredTheme());
  readonly currentTheme$ = this.theme$.asObservable();

  constructor() {
    this.applyTheme(this.theme$.value);
  }

  toggle(): void {
    const next: Theme = this.theme$.value === 'dark' ? 'light' : 'dark';
    this.setTheme(next);
  }

  setTheme(theme: Theme): void {
    localStorage.setItem(STORAGE_KEY, theme);
    this.theme$.next(theme);
    this.applyTheme(theme);
  }

  private applyTheme(theme: Theme | null): void {
    if (theme) {
      document.documentElement.setAttribute('data-theme', theme);
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }

  private readStoredTheme(): Theme | null {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'light' || stored === 'dark' ? stored : null;
  }
}
