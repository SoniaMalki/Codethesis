import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-clickable-icon',
  template: `
    <div class="icon-wrapper">
      <a [href]="rowData?.url" target="_blank"><i [class]="icon"></i></a>
    </div>
  `,
  styles: [`
    .icon-wrapper {
      display: flex;
      justify-content: center;
      align-items: center; 
      height: 100%;
    }
    a {
      display: flex;
    }
  `]
})
export class ClickableIconComponent {
  @Input() rowData: any;
  @Input() icon: string;
}
