import { Component, Input } from '@angular/core';

export type BrandSize = 'sm' | 'lg';

@Component({
  selector: 'app-brand',
  standalone: true,
  template: `
    <span class="brand" [class.brand--sm]="size === 'sm'">PATH</span>
    @if (tagline && size === 'lg') {
      <p class="brand-tagline">{{ tagline }}</p>
    }
  `,
  styleUrl: './brand.component.scss',
})
export class BrandComponent {
  @Input() size: BrandSize = 'lg';
  @Input() tagline?: string;
}
