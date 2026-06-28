import { DatePipe, DecimalPipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';

import { CardComponent } from '../../shared/ui/card/card.component';
import { Reflection } from '../../core/models/reflection.model';
import { ReflectionService } from '../../core/services/reflection.service';

@Component({
  selector: 'app-reflection',
  standalone: true,
  imports: [CardComponent, DecimalPipe, DatePipe],
  templateUrl: './reflection.component.html',
  styleUrl: './reflection.component.scss',
})
export class ReflectionComponent implements OnInit {
  private reflectionService = inject(ReflectionService);

  reflection: Reflection | null = null;
  loading = true;

  ngOnInit(): void {
    this.reflectionService.loadPrevious().subscribe((reflection) => {
      this.reflection = reflection;
      this.loading = false;
    });
  }

  get monthDate(): Date | null {
    if (!this.reflection) return null;
    return new Date(this.reflection.year, this.reflection.month - 1, 1);
  }
}
