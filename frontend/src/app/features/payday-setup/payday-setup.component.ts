import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { ButtonComponent } from '../../shared/ui/button/button.component';
import { CardComponent } from '../../shared/ui/card/card.component';
import { InputComponent } from '../../shared/ui/input/input.component';
import { BrandComponent } from '../../shared/ui/brand/brand.component';
import { PlanService } from '../../core/services/plan.service';

@Component({
  selector: 'app-payday-setup',
  standalone: true,
  imports: [ReactiveFormsModule, ButtonComponent, CardComponent, InputComponent, BrandComponent],
  templateUrl: './payday-setup.component.html',
  styleUrl: './payday-setup.component.scss',
})
export class PaydaySetupComponent {
  private fb = inject(FormBuilder);
  private planService = inject(PlanService);
  private router = inject(Router);

  form = this.fb.group({
    salary: ['', [Validators.required, Validators.pattern(/^\d+(\.\d{1,2})?$/)]],
  });

  submitting = false;
  serverError: string | null = null;

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const salary = Number(this.form.getRawValue().salary);
    this.submitting = true;
    this.serverError = null;

    this.planService.saveSalary(salary).subscribe({
      next: () => this.router.navigate(['/monthly-planning']),
      error: () => {
        this.submitting = false;
        this.serverError = 'We could not save that. Please try again.';
      },
    });
  }
}
