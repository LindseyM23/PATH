import { DecimalPipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NgIcon } from '@ng-icons/core';
import { forkJoin } from 'rxjs';

import { ButtonComponent } from '../../shared/ui/button/button.component';
import { CardComponent } from '../../shared/ui/card/card.component';
import { InputComponent } from '../../shared/ui/input/input.component';
import { Allocation } from '../../core/models/allocation.model';
import { CATEGORY_GROUP_LABELS, CategoryGroup } from '../../core/models/category.model';
import { AllocationService } from '../../core/services/allocation.service';
import { PlanService } from '../../core/services/plan.service';

interface CategoryGroupSection {
  label: string;
  allocations: Allocation[];
}

@Component({
  selector: 'app-monthly-planning',
  standalone: true,
  imports: [ReactiveFormsModule, ButtonComponent, CardComponent, InputComponent, DecimalPipe, NgIcon],
  templateUrl: './monthly-planning.component.html',
  styleUrl: './monthly-planning.component.scss',
})
export class MonthlyPlanningComponent implements OnInit {
  private fb = inject(FormBuilder);
  private planService = inject(PlanService);
  private allocationService = inject(AllocationService);
  private router = inject(Router);

  form = this.fb.group({});
  sections: CategoryGroupSection[] = [];
  salary = 0;
  submitting = false;
  loading = true;
  serverError: string | null = null;

  ngOnInit(): void {
    forkJoin({
      plan: this.planService.fetchCurrent(),
      allocations: this.allocationService.loadCurrent(),
    }).subscribe({
      next: ({ plan, allocations }) => {
        if (!plan) {
          this.router.navigate(['/payday-setup']);
          return;
        }
        this.salary = Number(plan.salary_amount);
        this.buildForm(allocations);
        this.loading = false;
      },
      error: () => {
        this.router.navigate(['/payday-setup']);
      },
    });
  }

  get allocatedTotal(): number {
    return Object.values(this.form.value).reduce(
      (sum: number, value) => sum + (Number(value) || 0),
      0,
    );
  }

  get remaining(): number {
    return this.salary - this.allocatedTotal;
  }

  submit(): void {
    const items = Object.entries(this.form.value).map(([categoryId, amount]) => ({
      category_id: categoryId,
      allocated_amount: Number(amount) || 0,
    }));

    this.submitting = true;
    this.serverError = null;

    this.allocationService.save(items).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: () => {
        this.submitting = false;
        this.serverError = 'We could not save your allocations. Please try again.';
      },
    });
  }

  private buildForm(allocations: Allocation[]): void {
    const sectionsByGroup = new Map<CategoryGroup, Allocation[]>();
    for (const allocation of allocations) {
      this.form.addControl(allocation.category_id, this.fb.control(allocation.allocated_amount));
      const existing = sectionsByGroup.get(allocation.group) ?? [];
      existing.push(allocation);
      sectionsByGroup.set(allocation.group, existing);
    }

    this.sections = Array.from(sectionsByGroup.entries()).map(([group, groupAllocations]) => ({
      label: CATEGORY_GROUP_LABELS[group],
      allocations: groupAllocations,
    }));
  }
}
