import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { ButtonComponent } from '../../../shared/ui/button/button.component';
import { CardComponent } from '../../../shared/ui/card/card.component';
import { InputComponent } from '../../../shared/ui/input/input.component';
import { BrandComponent } from '../../../shared/ui/brand/brand.component';
import { AuthService } from '../../../core/services/auth.service';
import { PlanService } from '../../../core/services/plan.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    ButtonComponent,
    CardComponent,
    InputComponent,
    BrandComponent,
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private planService = inject(PlanService);
  private router = inject(Router);

  form = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });

  submitting = false;
  serverError: string | null = null;

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const { email, password } = this.form.getRawValue();
    this.submitting = true;
    this.serverError = null;

    this.authService.login(email!, password!).subscribe({
      next: () => {
        this.planService.fetchCurrent().subscribe((plan) => {
          this.router.navigate([plan ? '/dashboard' : '/payday-setup']);
        });
      },
      error: () => {
        this.submitting = false;
        this.serverError = 'That email and password combination did not work.';
      },
    });
  }
}
