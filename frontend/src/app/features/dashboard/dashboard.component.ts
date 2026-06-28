import { DecimalPipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { ButtonComponent } from '../../shared/ui/button/button.component';
import { CardComponent } from '../../shared/ui/card/card.component';
import { InputComponent } from '../../shared/ui/input/input.component';
import { CATEGORY_GROUP_LABELS, Category, CategoryGroup } from '../../core/models/category.model';
import { MonthlyPlan } from '../../core/models/monthly-plan.model';
import { AllocationService } from '../../core/services/allocation.service';
import { CategoryService } from '../../core/services/category.service';
import { PlanService } from '../../core/services/plan.service';

interface CategoryOptionGroup {
  label: string;
  categories: Category[];
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CardComponent, DecimalPipe, RouterLink, ReactiveFormsModule, InputComponent, ButtonComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  private fb = inject(FormBuilder);
  private planService = inject(PlanService);
  private categoryService = inject(CategoryService);
  private allocationService = inject(AllocationService);
  private router = inject(Router);

  plan: MonthlyPlan | null = null;
  loading = true;

  quickLogOpen = false;
  quickLogSubmitting = false;
  categoryOptionGroups: CategoryOptionGroup[] = [];
  quickLogForm = this.fb.group({
    categoryId: [''],
    amount: [''],
  });

  ngOnInit(): void {
    this.planService.fetchCurrent().subscribe((plan) => {
      if (!plan) {
        this.router.navigate(['/payday-setup']);
        return;
      }
      this.plan = plan;
      this.loading = false;
    });

    this.categoryService.loadCategories().subscribe((categories) => {
      this.categoryOptionGroups = this.groupCategories(categories);
      const firstCategoryId = categories[0]?.id ?? '';
      this.quickLogForm.patchValue({ categoryId: firstCategoryId });
    });
  }

  openQuickLog(): void {
    this.quickLogOpen = true;
  }

  closeQuickLog(): void {
    this.quickLogOpen = false;
    this.quickLogForm.patchValue({ amount: '' });
  }

  submitQuickLog(): void {
    const { categoryId, amount } = this.quickLogForm.getRawValue();
    const numericAmount = Number(amount);
    if (!categoryId || !numericAmount || numericAmount <= 0) {
      return;
    }

    this.quickLogSubmitting = true;
    this.allocationService.quickLog(categoryId, numericAmount).subscribe({
      next: () => {
        this.planService.fetchCurrent().subscribe((plan) => {
          this.plan = plan;
          this.quickLogSubmitting = false;
          this.closeQuickLog();
        });
      },
      error: () => {
        this.quickLogSubmitting = false;
      },
    });
  }

  private groupCategories(categories: Category[]): CategoryOptionGroup[] {
    const byGroup = new Map<CategoryGroup, Category[]>();
    for (const category of categories) {
      const existing = byGroup.get(category.group) ?? [];
      existing.push(category);
      byGroup.set(category.group, existing);
    }
    return Array.from(byGroup.entries()).map(([group, groupCategories]) => ({
      label: CATEGORY_GROUP_LABELS[group],
      categories: groupCategories,
    }));
  }
}
