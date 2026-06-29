import { Component, EventEmitter, Output, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { NgIcon } from '@ng-icons/core';
import { Observable, map } from 'rxjs';

import { BrandComponent } from '../../shared/ui/brand/brand.component';
import { ThemeService } from '../../core/services/theme.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [NgIcon, BrandComponent, AsyncPipe],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
})
export class HeaderComponent {
  private readonly themeService = inject(ThemeService);

  @Output() toggleNav = new EventEmitter<void>();

  readonly isDark$: Observable<boolean> = this.themeService.currentTheme$.pipe(
    map((theme) => theme === 'dark'),
  );

  toggleTheme(): void {
    this.themeService.toggle();
  }
}
