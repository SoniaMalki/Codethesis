import { Component, Input, Output, EventEmitter } from '@angular/core';
import { LocalDataSource } from 'ng2-smart-table';

import { SmartTableData } from '../../../@core/data/smart-table';
import { ClickableIconComponent } from '../../tables/clickable-icon/clickable-icon.component';

import { DataSampleFileIconComponent } from '../../data-samples-view/data-sample-preview-icon/data-sample-edit-icon-component';
import { DataSamplePlayIconComponent } from '../../data-samples-view/data-sample-execute-icon/data-sample-edit-icon-component';
import { DataSampleEditIconComponent } from '../../data-samples-view/data-sample-edit-icon/data-sample-edit-icon-component';
import { DataSampleDeleteIconComponent } from '../../data-samples-view/data-sample-delete-icon/data-sample-delete-icon.component';

@Component({
  selector: 'ngx-smart-table',
  templateUrl: './smart-table.component.html',
  styleUrls: ['./smart-table.component.scss'],
})
export class SmartTableComponent {

  private _data: any[] = [];

  @Output() onDelete = new EventEmitter<any>();
  @Output() onEdit = new EventEmitter<any>();
  @Output() onExecute = new EventEmitter<any>();
  @Output() onCreate = new EventEmitter<any>();

  @Input() set data(data: any[]) {
    if (data) {
      this._data = data;
      this.source.load(data); 
      console.log('Data loaded:', data);
    }
  }

  settings = {
    add: {
      addButtonContent: '<i class="nb-plus"></i>',
      createButtonContent: '<i class="nb-checkmark"></i>',
      cancelButtonContent: '<i class="nb-close"></i>',
    },
    edit: {
      editButtonContent: '<i class="nb-edit"></i>',
      saveButtonContent: '<i class="nb-checkmark"></i>',
      cancelButtonContent: '<i class="nb-close"></i>',
      confirmSave: true,
    },
    delete: {
      deleteButtonContent: '<i class="nb-trash"></i>',
      confirmDelete: true,
    },
    actions: {
      add: false,
      edit: false,
      delete: false,
      position: 'right',
    },
    filter: false,
    columns: {
      id: {
        title: 'Id',
        type: 'string',
        width: '20px',
        class: 'column-id'
      },
      tasksetAction: {
        title: 'Actions',
        type: 'string',
        width: '80px',
        valuePrepareFunction: (cell, row) => {
          return row.taskset.action.charAt(0).toUpperCase() + " - " + row.assignment.action.charAt(0).toUpperCase() + " - " + row.scheduling.action.charAt(0).toUpperCase();
        }
      },
      tasksetNbrCore: {
        title: 'Cores number',
        type: 'string',
        width: '80px',
        valuePrepareFunction: (cell, row) => {
          if (row.taskset && row.taskset.parametersRetrieved && row.taskset.parametersRetrieved.numberOfCores){
            return row.taskset.parametersRetrieved.numberOfCores;
          } else {
            return "N/A";
          }
        }
      },
      taskPerTaskset: {
        title: 'Task per taskset',
        type: 'string',
        width: '80px',
        valuePrepareFunction: (cell, row) => {
          if (row.taskset && row.taskset.parametersRetrieved && row.taskset.parametersRetrieved.listOfTasksPerTaskset){
            return row.taskset.parametersRetrieved.listOfTasksPerTaskset;
          } else {
            return "N/A";
          }
        } 
      },
      tasksetCount: {
        title: 'Taskset count',
        type: 'string',
        width: '80px',
        valuePrepareFunction: (cell, row) => {
          if (row.taskset && row.taskset.parametersRetrieved && row.taskset.parametersRetrieved.tasksetCount){
            return row.taskset.parametersRetrieved.tasksetCount;
          } else {
            return "N/A";
          }
        }
      },
      assignmentMethod: {
        title: 'Assignment method',
        type: 'string',
        width: '80px',
        valuePrepareFunction: (cell, row) => {
          if (row.assignment && row.assignment.parametersRetrieved && row.assignment.parametersRetrieved.assignmentMethod) {
            if (row.assignment.parametersRetrieved.assignmentMethod == 'CITTA') {
              const paramsArray = row.assignment.parametersRetrieved.cittaCriteria;
          
              if (paramsArray.length === 0) {
                return row.assignment.parametersRetrieved.assignmentMethod.toUpperCase();
              } else {
                const joinedString = paramsArray.map(element => element.toUpperCase()).join(', ');
                return row.assignment.parametersRetrieved.assignmentMethod.toUpperCase() + " (" + (joinedString.length > 14 ? joinedString.substring(0, 14) + '..' : joinedString) + ')';
              }
            } else {
              return row.assignment.parametersRetrieved.assignmentMethod.toUpperCase();
            }
          } else {
            return "N/A";
          }
        }
      },
      schedulingAlgorithm: {
        title: 'Scheduling algorithm',
        type: 'string',
        width: '80px',
        valuePrepareFunction: (cell, row) => {
          if (row.scheduling && row.scheduling.parametersRetrieved && row.scheduling.parametersRetrieved.schedulingAlgorithms) {
            console.log(row.scheduling.parametersRetrieved.schedulingAlgorithms);
            const paramsArray = row.scheduling.parametersRetrieved.schedulingAlgorithms;
            console.log(paramsArray);
            if (paramsArray && Array.isArray(paramsArray)) {
              const joinedString = paramsArray.map(element => element.toUpperCase()).join(', ');

              return joinedString.length > 14 ? joinedString.substring(0, 14) + '..' : joinedString;
            }
          }
          
          return "N/A";
        }
      },
      preview: {
        title: 'Preview',
        type: 'custom',
        renderComponent: DataSampleFileIconComponent,
        onComponentInitFunction: (instance) => {
          instance.editRequest.subscribe((rowData) => {
            this.onEditConfirm(rowData);
          });
        },
        width: '40px',
      },
      execute: {
        title: 'Execute',
        type: 'custom',
        renderComponent: DataSamplePlayIconComponent,
        onComponentInitFunction: (instance) => {
          instance.editRequest.subscribe((rowData) => {
            this.onExecuteConfirm(rowData);
          });
        },
        width: '40px',
      },
      customEdit: {
        title: 'Edit',
        type: 'custom',
        renderComponent: DataSampleEditIconComponent,
        onComponentInitFunction: (instance) => {
          instance.editRequest.subscribe((rowData) => {
            this.onEditConfirm(rowData);
          });
        },
        width: '40px',
      },
      customDelete: {
        title: 'Delete',
        type: 'custom',
        renderComponent: DataSampleDeleteIconComponent,
        onComponentInitFunction: (instance) => {
          instance.deleteRequest.subscribe((rowData) => {
            this.onDeleteConfirm(rowData);
          });
        },
        width: '40px',
      },
    },
    pager: {
      display: true,
      perPage: 20 
    }
  };

  source: LocalDataSource = new LocalDataSource();

  constructor(private service: SmartTableData) {}

  onCreateConfirm(): void {
    this.onCreate.emit();
  }

  onEditConfirm(rowData: any): void {
    this.onEdit.emit(rowData);
  }

  onExecuteConfirm(rowData: any): void {
    this.onExecute.emit(rowData);
  }

  onDeleteConfirm(rowData: any): void {
    this.onDelete.emit(rowData);
  }
}
