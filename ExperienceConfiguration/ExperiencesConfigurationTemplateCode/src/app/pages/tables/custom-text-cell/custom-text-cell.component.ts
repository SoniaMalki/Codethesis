import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-custom-text-cell',
  template: `<div [ngStyle]="{'font-weight': fontWeight}">{{ text }}</div>`
})
export class CustomTextCellComponent {
  @Input() text: string = '';
  @Input() fontWeight: string = 'normal';  // You can set the default font weight here
}
