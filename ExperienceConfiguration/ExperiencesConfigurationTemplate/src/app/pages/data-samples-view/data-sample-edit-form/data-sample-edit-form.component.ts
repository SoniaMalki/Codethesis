import { Component, EventEmitter, Input, Output, OnInit, TemplateRef  } from '@angular/core';
import { HttpClient } from '@angular/common/http'; // Import HttpClient for making HTTP requests
import { NbDialogService } from '@nebular/theme';
import { Observable } from 'rxjs';

@Component({
  selector: 'ngx-data-sample-edit-form',
  templateUrl: './data-sample-edit-form.component.html',
  styleUrls: ['./data-sample-edit-form.component.scss']
})
export class DataSampleEditFormComponent {
  @Output() onSave = new EventEmitter<void>();
  @Output() onCancel = new EventEmitter<void>();
  @Input() rowData: any;



  actionGenerate = "generate"
  actionOpen = "open"
  actionNone = "none"

  tasksetActions: string[]
  assignmentActions: string[] 
  schedulingActions: string[] 

  translationResultInstruction: string;
  translationResultInput: string;
  translationResultOutput: string;
  translationResultAdditionalInfo: string;
  
  constructor(private dialogService: NbDialogService) {}

  numberOfCores = Array.from({length: 20}, (_, i) => i + 1); // Creates an array [1, 2, ..., 10]
  listOfMaxUtilizations = Array.from({length: 10}, (_, i) => this.formatNumber((i+1) * 0.1)); // Creates an array [1, 2, ..., 10]
  listOfTaskPerTaskset = Array.from({length: 20}, (_, i) => i + 1 ); // Creates an array [1, 2, ..., 10]
  tasksetCount = Array.from({length: 20}, (_, i) => i + 1); // Creates an array [1, 2, ..., 10]
  listOfInterferenceFactors = Array.from({length: 6}, (_, i) => this.formatNumber(i * 0.2) ); // Creates an array [1, 2, ..., 10]
  listOfPeriodGenerationMethods = ["unif", "logunif", "prime_matrix"]

  assignmentMethods = ["citta", "ffdu"]
  cittaCriterias = ["et", "big"]

  schedulingAlgorithms = ["edf", "dm"] 



  ngOnInit() {
    // Initialize model from rowData on input change
    console.log(this.rowData)
    this.initializeForm();
  }

  initializeForm() {
    this.tasksetActions = [this.actionGenerate, this.actionOpen];
    this.assignmentActions = [this.actionGenerate, this.actionOpen, this.actionNone];
    this.schedulingActions = [this.actionGenerate, this.actionOpen, this.actionNone];
    
    if (this.rowData) {
      if (this.rowData.taskset.action == this.actionGenerate) {
        this.assignmentActions = [this.actionGenerate, this.actionNone];
        this.schedulingActions = [this.actionGenerate, this.actionNone];
      }
    }
  }
  

  formatNumber(value: number): number {
    const formatted = value.toFixed(1);
    return parseFloat(formatted);
  }

  capitalizeFirstLetter(action: string): string {
    return action.charAt(0).toUpperCase() + action.slice(1);
  }

  onTasksetActionChange(newAction: string): void {
    if (newAction == this.actionGenerate) {
      this.assignmentActions = [this.actionGenerate, this.actionNone];
      this.schedulingActions = [this.actionGenerate, this.actionNone];

      if (this.rowData.assignment.action == this.actionOpen) {
        this.rowData.assignment.action = this.actionGenerate
      }

      if (this.rowData.scheduling.action == this.actionOpen) {
        this.rowData.scheduling.action = this.actionGenerate
      }

    } else if (newAction == this.actionOpen) {
      this.assignmentActions = [this.actionOpen, this.actionNone];
      this.schedulingActions = [this.actionOpen, this.actionNone];

      if (this.rowData.assignment.action == this.actionGenerate) {
        this.rowData.assignment.action = this.actionOpen
      }

      if (this.rowData.scheduling.action == this.actionGenerate) {
        this.rowData.scheduling.action = this.actionOpen
      }
    }
  }

  onAssignmentActionChange(newAction: string): void {
    if (newAction == this.actionGenerate) {
      this.schedulingActions = [this.actionGenerate, this.actionNone];

      if (this.rowData.scheduling.action == this.actionOpen) {
        this.rowData.scheduling.action = this.actionGenerate
      }

    } else if (newAction == this.actionOpen) {
      this.schedulingActions = [this.actionOpen, this.actionNone];

      if (this.rowData.scheduling.action == this.actionGenerate) {
        this.rowData.scheduling.action = this.actionOpen
      }
    } else if (newAction == this.actionNone) {
      this.schedulingActions = [this.actionNone];
      this.rowData.scheduling.action = this.actionNone
      
    }
  }

  onSchedulingActionChange(newValue: string): void {
    console.log('Action changed to:', newValue);
  }

  saveItem() {
  	if (window.confirm("Are you sure you want to save this item?")) {
  	  /*this.rowData.quality = this.quality/10
  	  this.rowData.positivityRating = this.positivityRating/10
  	  this.rowData.processed = this.processed == 'Yes' ? true : false  */
      this.onSave.emit();
      this.onCancel.emit();
    }
  }

  cancel() {
    this.onCancel.emit();
  }
}



