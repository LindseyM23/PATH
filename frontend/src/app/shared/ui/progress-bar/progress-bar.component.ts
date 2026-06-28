import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-progress-bar',
  standalone: true,
  template: `
    <div class="progress-track">
      <div class="progress-fill" [style.width.%]="percentage"></div>
    </div>
  `,
  styleUrl: './progress-bar.component.scss',
})
export class ProgressBarComponent {
  @Input() value = 0;
  @Input() max = 100;

  get percentage(): number {
    if (this.max <= 0) return 0;
    return Math.min(100, Math.max(0, (this.value / this.max) * 100));
  }
}
