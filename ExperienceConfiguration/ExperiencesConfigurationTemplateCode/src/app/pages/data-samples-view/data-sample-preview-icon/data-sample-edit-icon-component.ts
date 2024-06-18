import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { NbPopoverModule } from '@nebular/theme'; // Import the NbPopoverModule

@Component({
  selector: 'ngx-data-sample-edit-icon',
  templateUrl: './data-sample-edit-icon-component.html',
  styleUrls: ['./data-sample-edit-icon-component.scss']
})
export class DataSampleFileIconComponent{
	@Input() rowData: any;
  rowDataDup: any;
	@Output() editRequest = new EventEmitter<any>();

  ngOnInit(): void {
    this.transformData();
  }

  transformData(): void {
    // Deep cloning using JSON
    let clonedData = JSON.parse(JSON.stringify(this.rowData));
    
    // Deep cloning using lodash, if your data contains complex types
    // let clonedData = _.cloneDeep(this.rowData);

    // Rename and unset as specified
    if (clonedData.taskset && clonedData.taskset.parametersRetrieved) {
      clonedData.taskset.parameters = clonedData.taskset.parametersRetrieved;
      delete clonedData.taskset.parametersRetrieved;
    }

    if (clonedData.assignment && clonedData.assignment.parametersRetrieved) {
      clonedData.assignment.parameters = clonedData.assignment.parametersRetrieved;
      delete clonedData.assignment.parametersRetrieved;
    }

    if (clonedData.scheduling && clonedData.scheduling.parametersRetrieved) {
      clonedData.scheduling.parameters = clonedData.scheduling.parametersRetrieved;
      delete clonedData.scheduling.parametersRetrieved;
    }

    this.rowDataDup = clonedData
  }

	onEditClick(): void {

  }
}
