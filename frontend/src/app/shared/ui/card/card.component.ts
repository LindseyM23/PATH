import { Component, Input } from '@angular/core';

export type CardPadding = 'sm' | 'md' | 'lg';

@Component({
  selector: 'app-card',
  standalone: true,
  template: `
    <div class="card" [class]="'card--' + padding">
      <ng-content></ng-content>
    </div>
  `,
  styleUrl: './card.component.scss',
})
export class CardComponent {
  @Input() padding: CardPadding = 'md';
}
