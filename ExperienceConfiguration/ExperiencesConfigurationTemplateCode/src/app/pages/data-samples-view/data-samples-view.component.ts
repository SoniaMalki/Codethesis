import { Component, OnDestroy } from '@angular/core';
import {
  NbComponentStatus,
  NbGlobalLogicalPosition,
  NbGlobalPhysicalPosition,
  NbGlobalPosition,
  NbToastrService,
  NbToastrConfig,
} from '@nebular/theme';

import { NbThemeService } from '@nebular/theme';
import { takeWhile } from 'rxjs/operators' ;
import { SolarData } from '../../@core/data/solar';
import { DataSampleService } from '../../services/datasample.service';
import { SmartTableComponent } from '../tables/smart-table/smart-table.component'
import { DataSamplesRequest } from '../../models/data-samples-request.model';  
import { DataSamplesFilters } from '../../models/data-samples-filters.model';  
import { NbDialogService } from '@nebular/theme';
import { ShowcaseDialogComponent } from '../modal-overlays/dialog/showcase-dialog/showcase-dialog.component';
import { DeleteConfirmModalComponent } from './delete-confirm-modal/delete-confirm-modal.component'
import { DataSampleEditFormComponent } from './data-sample-edit-form/data-sample-edit-form.component'
import { DataSampleCreateFormComponent } from './data-sample-create-form/data-sample-create-form.component'


interface CardSettings {
  title: string;
  iconClass: string;
  type: string;
}

@Component({
  selector: 'ngx-dashboard',
  styleUrls: ['./data-samples-view.component.scss'],
  templateUrl: './data-samples-view.component.html',
})
export class DataSamplesViewComponent  {

  dashboardStatistics: any;

  tasksets: any[]
  assignments: any[]
  schedulings: any[]

  selectedSources: string[] = [];
  selectedReferences: string[] = [];
  selectedTags: string[] = [];

  selectedProcessedValue : boolean = false;
  selectedDeletedValue : boolean = false;
  dataList : any[] = []
  experiences: any[] = []
  experiencesLoaded: any[] = []
  sources: string[];
  references: string[];
  tags: string[];

  createRowData: any;
  rowDataEdit: any;


  sortByOptions = ['createdDate', 'updatedDate', 'quality', 'positivityRating', 'source', 'reference'];
  sortOrderOptions = ['asc', 'desc'];

  sortBy: string = 'createdDate';  
  sortOrder: string = 'asc';       


  constructor(public dataSampleService: DataSampleService, private dialogService: NbDialogService, private toastrService: NbToastrService) {
    this.fetchExperiences()
  }

  private fetchExperiences(): void {
    this.dataSampleService.getAllExperienceParameters().subscribe(
      (data: any) => {
        this.experiences = data;
        this.fetchTasksetData()
        console.log(data);
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }



  private fetchTasksetData(): void {
    this.dataSampleService.getAllTasksets().subscribe({
      next: (tasksets: any[]) => {
        this.tasksets = tasksets;
        this.experiences.forEach(exp => {
          const foundTaskset = tasksets.find(t => t.id === exp.taskset.tasksetId);
          if (foundTaskset) {
            exp.taskset.parametersRetrieved = foundTaskset;
          }
        });
        console.log(this.tasksets);
        console.log(this.experiences);
        this.fetchAssignmentData()
      },
      error: (error: any) => {
        console.error('Error fetching tasksets:', error);
      }
    });
  }


  private fetchAssignmentData(): void {
    this.dataSampleService.getAllAssignments().subscribe({
      next: (assignments: any[]) => {
        this.assignments = assignments;
        this.experiences.forEach(exp => {
          const foundAssignment = assignments.find(a => a.id === exp.assignment.assignmentId);
          if (foundAssignment) {
            exp.assignment.parametersRetrieved = foundAssignment;
          }
        });
        console.log(this.experiences);
        this.fetchSchedulingData()
      },
      error: (error: any) => {
        console.error('Error fetching assignments:', error);
      }
    });
  }

  private fetchSchedulingData(): void {
    this.dataSampleService.getAllSchedulings().subscribe({
      next: (schedulings: any[]) => {
        this.schedulings = schedulings;
        this.experiences.forEach(exp => {
          const foundScheduling = schedulings.find(s => s.id === exp.scheduling.schedulingId);
          if (foundScheduling) {
            exp.scheduling.parametersRetrieved = foundScheduling;
          }
        });
        console.log(this.experiences);
        this.experiencesLoaded = this.experiences
      },
      error: (error: any) => {
        console.error('Error fetching schedulings:', error);
      }
    });
  }


  onFieldChanged(): void {
    console.log("example")
    this.fetchExperiences()
  }



  onEditButtonClicked(rowData: any) {
    console.log('Edit data:', rowData);
    this.openEditModal(rowData)
  }


  onExecuteButtonClicked(rowData: any) {
    console.log('Execute button clicked', rowData);
    this.handleExecuteScript(rowData.id)
  }

  handleExecuteScript(number: number) {
    this.dataSampleService.executeScriptWithNumber(number).subscribe({
      next: (response) => {
        console.log('Execution success:', response);
      },
      error: (err) => {
        console.error('Error during script execution:', err);
      }
    });
}

  openCreateModal() {
    this.createRowData = {
      taskset: {
        action: "generate",
        parameters: {
          numberOfCores: 4,
          listOfMaxUtilization: [],
          listOfTasksPerTaskset: 5,
          tasksetCount: 3,
          listOfInterferenceFactors: [],
          listOfProbabilityFactors: [],
          minPeriod: 50,
          maxPeriod: 1000,
          listOfPeriodGenerationMethods: [],
          granularity: []
        },
        taskset_id: ""
      },
      assignment: {
        action: "generate",
        parameters: {
          assignmentMethod: "",
          cittaCriteria: []
        },
        taskset_id: "",
        assignment_id: ""
      },
      scheduling: {
        action: "generate",
        parameters: {
          schedulingAlgorithms: []
        },
        taskset_id: "",
        assignment_id: "",
        scheduling_id: ""
      },
    }

    let dialogRef = this.dialogService.open(DataSampleCreateFormComponent, {
      context: {
        rowData: this.createRowData,
        allTasksets: this.tasksets,
        allAssignments: this.assignments,
        allSchedulings: this.schedulings
      }, closeOnBackdropClick: false});

    dialogRef.onClose.subscribe(result => {
      // Handle dialog close with result
    });

    const subSoftDelete = dialogRef.componentRef.instance.onSave.subscribe(() => {
      this.handleCreate(this.createRowData);
    });

    const subCancel = dialogRef.componentRef.instance.onCancel.subscribe(() => {
      dialogRef.close();
    });

    dialogRef.onClose.subscribe(() => {
      subCancel.unsubscribe();
    });
  }



  openEditModal(rowData: any) {
    this.rowDataEdit = rowData
    if (this.rowDataEdit.taskset.action == "open") {
      this.rowDataEdit.taskset.parameters = {
        numberOfCores: 4,
        listOfMaxUtilization: [],
        listOfTasksPerTaskset: 5,
        tasksetCount: 3,
        listOfInterferenceFactors: [],
        listOfProbabilityFactors: [],
        minPeriod: 50,
        maxPeriod: 1000,
        listOfPeriodGenerationMethods: [],
        granularity: []
      }
    }
    

    this.rowDataEdit.assignment.parameters = {
      assignmentMethod: "",
      cittaCriteria: []
    }

    this.rowDataEdit.scheduling.parameters = {
      schedulingAlgorithms: []
    }


    let dialogRef = this.dialogService.open(DataSampleCreateFormComponent, {
      context: {
        rowData: this.rowDataEdit,
        allTasksets: this.tasksets,
        allAssignments: this.assignments,
        allSchedulings: this.schedulings
      }, closeOnBackdropClick: false});

    dialogRef.onClose.subscribe(result => {
      // Handle dialog close with result
    });

    const subSoftDelete = dialogRef.componentRef.instance.onSave.subscribe(() => {
      this.handleSave(rowData);
    });

    const subCancel = dialogRef.componentRef.instance.onCancel.subscribe(() => {
      dialogRef.close();
    });

    dialogRef.onClose.subscribe(() => {
      subSoftDelete.unsubscribe();
      subCancel.unsubscribe();
    });
  }

  onDeleteButtonClicked(rowData: any) {
    console.log('Deleted data:', rowData);
    this.openDeleteModal(rowData)
  }

  openDeleteModal(rowData: any) {
    let dialogRef = this.dialogService.open(DeleteConfirmModalComponent, {
      context: {
         // Ensure this is being passed correctly
      }});

    dialogRef.onClose.subscribe(result => {
      // Handle dialog close with result
    });

    const subDelete = dialogRef.componentRef.instance.onDelete.subscribe(() => {
      this.handleDelete(rowData);
    });

    const subCancel = dialogRef.componentRef.instance.onCancel.subscribe(() => {
      dialogRef.close();
    });

    dialogRef.onClose.subscribe(() => {
      // Cleanup subscriptions when the dialog is closed
      subDelete.unsubscribe();
      subCancel.unsubscribe();
    });
  }

  private showToast(type: NbComponentStatus, title: string, body: string) {
    const config = {
      status: type,
      destroyByClick: false,
      duration: 3000,
      hasIcon: false,
      position: NbGlobalPhysicalPosition.TOP_RIGHT,
      preventDuplicates: false,
    };
    const titleContent = title ? `${title}` : '';

    this.toastrService.show(
      body,
      titleContent,
      config);
  }

  handleCreate(rowData: any) {
    console.log('Create:', rowData);
    this.dataSampleService.createExperience(rowData).subscribe({
      next: (response) => {
        console.log('Create success:', response);
        this.showToast('success', 'Experience parameters created successfully', '');
        this.fetchExperiences(); 
      },
      error: (err) => {
        console.error('Error during create:', err);
        this.showToast('danger', 'Error while trying to create experience parameters', '');
        this.fetchExperiences(); 
      }
    });
  }

  handleSave(rowData: any) {
    console.log('Save:', rowData);
    this.dataSampleService.updateExperience(rowData.id, rowData).subscribe({
      next: (response) => {
        console.log('Update success:', response);
        this.showToast('success', 'Experience parameters updated successfully', '');
        this.fetchExperiences(); 
      },
      error: (err) => {
        console.error('Error during update:', err);
        this.showToast('danger', 'Error while trying to update experience parameters ', '');
        this.fetchExperiences(); 
      }
    });
  }



  handleDelete(rowData: any) {
    console.log('Delete:', rowData);
    this.dataSampleService.deleteExperience(rowData.id).subscribe({
      next: (response) => { console.log(response); this.showToast('success', 'Successfully deleted', ''); this.fetchExperiences() },
      error: (err) => { console.error('Error during delete:', err); ; this.showToast('danger', 'Error while trying to delete', ''); this.fetchExperiences() }
    });
    
  }
}
