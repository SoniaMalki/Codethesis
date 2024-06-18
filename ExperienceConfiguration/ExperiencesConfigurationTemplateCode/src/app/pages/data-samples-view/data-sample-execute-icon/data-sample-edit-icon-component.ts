import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'ngx-data-sample-edit-icon',
  templateUrl: './data-sample-edit-icon-component.html',
  styleUrls: ['./data-sample-edit-icon-component.scss']
})
export class DataSamplePlayIconComponent{
	@Input() rowData: any;
	@Output() editRequest = new EventEmitter<any>();

	onEditClick(): void {
    console.log(this.rowData);
    this.editRequest.emit(this.rowData);
    // Additional logic for what should happen on click can be added here
  }
}
