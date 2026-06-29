import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { NgIcon } from '@ng-icons/core';

import { AuthService } from '../../core/services/auth.service';

interface NavLink {
  path: string;
  label: string;
  icon: string;
}

@Component({
  selector: 'app-side-nav',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, NgIcon],
  templateUrl: './side-nav.component.html',
  styleUrl: './side-nav.component.scss',
})
export class SideNavComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  @Input() open = false;
  @Output() closeNav = new EventEmitter<void>();

  readonly links: NavLink[] = [
    { path: '/dashboard', label: 'Dashboard', icon: 'lucideLayoutDashboard' },
    { path: '/monthly-planning', label: 'Monthly Planning', icon: 'lucideWallet' },
    { path: '/goals', label: 'Goals', icon: 'lucideTarget' },
    { path: '/reflection', label: 'Reflection', icon: 'lucideMessageCircle' },
  ];

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
