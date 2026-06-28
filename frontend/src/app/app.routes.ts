import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./features/auth/register/register.component').then((m) => m.RegisterComponent),
  },
  {
    path: 'payday-setup',
    loadComponent: () =>
      import('./features/payday-setup/payday-setup.component').then((m) => m.PaydaySetupComponent),
    canActivate: [authGuard],
  },
  {
    path: 'monthly-planning',
    loadComponent: () =>
      import('./features/monthly-planning/monthly-planning.component').then(
        (m) => m.MonthlyPlanningComponent,
      ),
    canActivate: [authGuard],
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
    canActivate: [authGuard],
  },
  {
    path: 'goals',
    loadComponent: () => import('./features/goals/goals.component').then((m) => m.GoalsComponent),
    canActivate: [authGuard],
  },
  {
    path: 'reflection',
    loadComponent: () =>
      import('./features/reflection/reflection.component').then((m) => m.ReflectionComponent),
    canActivate: [authGuard],
  },
  { path: '**', redirectTo: 'login' },
];
