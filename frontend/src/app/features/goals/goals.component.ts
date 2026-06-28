import { DecimalPipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { ButtonComponent } from '../../shared/ui/button/button.component';
import { CardComponent } from '../../shared/ui/card/card.component';
import { InputComponent } from '../../shared/ui/input/input.component';
import { ProgressBarComponent } from '../../shared/ui/progress-bar/progress-bar.component';
import { Goal } from '../../core/models/goal.model';
import { GoalService } from '../../core/services/goal.service';

@Component({
  selector: 'app-goals',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    ButtonComponent,
    CardComponent,
    InputComponent,
    ProgressBarComponent,
    DecimalPipe,
  ],
  templateUrl: './goals.component.html',
  styleUrl: './goals.component.scss',
})
export class GoalsComponent implements OnInit {
  private fb = inject(FormBuilder);
  private goalService = inject(GoalService);

  goals: Goal[] = [];
  loading = true;
  creating = false;
  serverError: string | null = null;

  openContributeFor: string | null = null;
  contributeSubmitting = false;

  createForm = this.fb.group({
    name: ['', Validators.required],
    targetAmount: ['', [Validators.required, Validators.pattern(/^\d+(\.\d{1,2})?$/)]],
  });

  contributeForm = this.fb.group({
    amount: [''],
  });

  ngOnInit(): void {
    this.goalService.loadGoals().subscribe((goals) => {
      this.goals = goals;
      this.loading = false;
    });
  }

  createGoal(): void {
    if (this.createForm.invalid) {
      this.createForm.markAllAsTouched();
      return;
    }

    const { name, targetAmount } = this.createForm.getRawValue();
    this.creating = true;
    this.serverError = null;

    this.goalService.create(name!, Number(targetAmount)).subscribe({
      next: (goal) => {
        this.goals = [...this.goals, goal];
        this.creating = false;
        this.createForm.reset();
      },
      error: () => {
        this.creating = false;
        this.serverError = 'We could not create that goal. Please try again.';
      },
    });
  }

  openContribute(goalId: string): void {
    this.openContributeFor = goalId;
    this.contributeForm.reset();
  }

  closeContribute(): void {
    this.openContributeFor = null;
  }

  submitContribute(goalId: string): void {
    const amount = Number(this.contributeForm.getRawValue().amount);
    if (!amount || amount <= 0) {
      return;
    }

    this.contributeSubmitting = true;
    this.goalService.contribute(goalId, amount).subscribe({
      next: (updated) => {
        this.goals = this.goals.map((g) => (g.id === updated.id ? updated : g));
        this.contributeSubmitting = false;
        this.closeContribute();
      },
      error: () => {
        this.contributeSubmitting = false;
      },
    });
  }

  removeGoal(goalId: string): void {
    this.goalService.remove(goalId).subscribe(() => {
      this.goals = this.goals.filter((g) => g.id !== goalId);
    });
  }
}
