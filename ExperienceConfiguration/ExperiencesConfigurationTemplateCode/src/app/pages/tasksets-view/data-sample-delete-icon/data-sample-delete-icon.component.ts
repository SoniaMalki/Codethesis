import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'ngx-data-sample-delete-icon',
  templateUrl: './data-sample-delete-icon.component.html',
  styleUrls: ['./data-sample-delete-icon.component.scss']
})
export class DataSampleDeleteIconComponent {
	@Input() rowData: any;
	@Output() deleteRequest = new EventEmitter<any>();

	onDeleteClick(): void {
		console.log("example")
    console.log(this.rowData);
    this.deleteRequest.emit(this.rowData);
    // Additional logic for what should happen on click can be added here
  }
}
