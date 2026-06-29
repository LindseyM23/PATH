import { Component, OnDestroy, inject } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { Subscription, filter } from 'rxjs';

import { HeaderComponent } from '../header/header.component';
import { SideNavComponent } from '../side-nav/side-nav.component';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, SideNavComponent],
  templateUrl: './shell.component.html',
  styleUrl: './shell.component.scss',
})
export class ShellComponent implements OnDestroy {
  private readonly router = inject(Router);
  private readonly navigationSub: Subscription;

  navOpen = false;

  constructor() {
    this.navigationSub = this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe(() => {
        this.navOpen = false;
      });
  }

  ngOnDestroy(): void {
    this.navigationSub.unsubscribe();
  }
}
