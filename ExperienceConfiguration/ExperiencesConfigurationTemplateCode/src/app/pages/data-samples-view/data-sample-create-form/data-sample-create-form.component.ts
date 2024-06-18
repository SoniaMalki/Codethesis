import { Component, EventEmitter, Input, Output, OnInit, TemplateRef  } from '@angular/core';
import { NbDialogService } from '@nebular/theme';
import { Observable } from 'rxjs';
import { DataSampleService } from '../../../services/datasample.service';

@Component({
  selector: 'ngx-data-sample-create-form',
  templateUrl: './data-sample-create-form.component.html',
  styleUrls: ['./data-sample-create-form.component.scss']
})
export class DataSampleCreateFormComponent {
  @Output() onSave = new EventEmitter<void>();
  @Output() onCancel = new EventEmitter<void>();

  @Input() rowData: any;

  @Input() allTasksets: any[];
  @Input() allAssignments: any[];
  @Input() allSchedulings: any[];

  tasksets: any[];
  assignments: any[];
  schedulings: any[];

  actionGenerate = 'generate';
  actionOpen = 'open';
  actionNone = 'none';

  tasksetActions: string[];
  assignmentActions: string[];
  schedulingActions: string[];

  translationResultInstruction: string;
  translationResultInput: string;
  translationResultOutput: string;
  translationResultAdditionalInfo: string;
  
  constructor(private dialogService: NbDialogService, public dataSampleService: DataSampleService) {}

  numberOfCores = [2, 4, 8];
  listOfMaxUtilizations = Array.from({ length: 5 }, (_, i) => this.formatNumber((i + 1) * 0.2));
  listOfTaskPerTaskset = [10, 20];
  tasksetCount = [1, 2, 4, 8, 16];
  listOfInterferenceFactors = [0.2, 0.8];
  listOfProbabilityFactors = [0.1, 0.4];

  assignmentMethods = ['CITTA', 'WFDU', 'FFDU', 'W_min'];
  cittaCriterias = [
    'WCET_ascending', 'WCET_descending',
    'Period_ascending', 'Period_descending',
    'Utilization_ascending', 'Utilization_descending',
    'Execution_Slack_ascending', 'Execution_Slack_descending',
    'Random_order_ascending', 'Random_order_descending'
  ];

  schedulingAlgorithms = ['RHMA', 'EDF', 'DM', 'Combined Scheduler'];
  showDetailsTaskset = [];
  showDetailsAssignment = [];
  showDetailsScheduling = [];

  selectedTasksetId: number;
  selectedAssignmentId: number;
  selectedSchedulingId: number;

  ngOnInit() {
    // Initialize model from rowData on input change
    console.log(this.rowData);
    console.log(this.tasksets);
    console.log(this.assignments);
    console.log(this.schedulings);
    console.log(this.selectedTasksetId);

    this.tasksets = this.allTasksets;
    this.assignments = this.allAssignments;
    this.schedulings = this.allSchedulings;

    this.initializeForm();
    this.tasksets.forEach((_, index) => (this.showDetailsTaskset[index] = false));
    this.assignments.forEach((_, index) => (this.showDetailsAssignment[index] = false));
    this.schedulings.forEach((_, index) => (this.showDetailsScheduling[index] = false));

    if (this.rowData) {
      if (this.rowData.taskset && this.rowData.taskset.action == 'open') {
        console.log('example taskset');
        this.selectedTasksetId = this.rowData.taskset.tasksetId;
      }
      if (this.rowData.assignment && this.rowData.assignment.action == 'open') {
        console.log('example assignment');
        this.selectedAssignmentId = this.rowData.assignment.assignmentId;
      }
      if (this.rowData.scheduling && this.rowData.scheduling.action == 'open') {
        console.log('example scheduling');
        this.selectedSchedulingId = this.rowData.scheduling.schedulingId;
      }
    }

    console.log(this.selectedTasksetId, this.selectedAssignmentId, this.selectedSchedulingId);
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

  private filterByTasksetId(tasksetId: number): void {
    this.dataSampleService.filterByTasksetId(tasksetId).subscribe(
      (data: any) => {
        console.log(data);
        this.assignments = data.assignmentParameters;
        this.schedulings = data.schedulingParameters;

        const assignmentIds = this.assignments.map((s) => s.id);
        if (!assignmentIds.includes(this.selectedAssignmentId)) {
          this.selectedAssignmentId = undefined;
        }

        const schedulingIds = this.schedulings.map((s) => s.id);
        if (!schedulingIds.includes(this.selectedSchedulingId)) {
          this.selectedSchedulingId = undefined;
        }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  private filterByAssignmentId(assignmentId: number): void {
    this.dataSampleService.filterByAssignmentId(assignmentId).subscribe(
      (data: any) => {
        console.log(data);
        this.schedulings = data;
        const schedulingIds = this.schedulings.map((s) => s.id);
        if (!schedulingIds.includes(this.selectedSchedulingId)) {
          this.selectedSchedulingId = undefined;
        }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  selectTaskset(tasksetId: number): void {
    if (this.selectedTasksetId == tasksetId) {
      this.selectedTasksetId = undefined;
      this.assignments = this.allAssignments;
      this.schedulings = this.allSchedulings;
      console.log('Unselect Taskset ID: ', this.selectedTasksetId);
    } else {
      this.selectedTasksetId = tasksetId;
      this.filterByTasksetId(tasksetId);

      console.log('Selected Taskset ID: ', this.selectedTasksetId);
    }
  }

  selectAssignment(assignmentId: number): void {
    if (this.selectedAssignmentId == assignmentId) {
      this.selectedAssignmentId = undefined;
      this.schedulings = this.allSchedulings;
      console.log('Unselect Assignment ID: ', this.selectedAssignmentId);
    } else {
      this.selectedAssignmentId = assignmentId;
      this.filterByAssignmentId(assignmentId);
      console.log('Selected Assignment ID: ', this.selectedAssignmentId);
    }
  }

  selectScheduling(schedulingId: number): void {
    if (this.selectedSchedulingId == schedulingId) {
      this.selectedSchedulingId = undefined;
      console.log('Unselect Scheduling ID: ', this.selectedSchedulingId);
    } else {
      this.selectedSchedulingId = schedulingId;
      console.log('Selected Scheduling ID: ', this.selectedSchedulingId);
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
    this.rowData.taskset.action = newAction;
    if (newAction == this.actionGenerate) {
      this.selectedTasksetId = null;
      this.assignmentActions = [this.actionGenerate, this.actionNone];
      this.schedulingActions = [this.actionGenerate, this.actionNone];

      if (this.rowData.assignment.action == this.actionOpen) {
        this.onAssignmentActionChange(this.actionGenerate);
      }
    } else if (newAction == this.actionOpen) {
      this.assignmentActions = [this.actionGenerate, this.actionOpen, this.actionNone];
    }
  }

  toggleDetailsTaskset(index: number, event: MouseEvent): void {
    event.stopPropagation();
    this.showDetailsTaskset[index] = !this.showDetailsTaskset[index];
    console.log(this.showDetailsTaskset);
  }

  toggleDetailsAssignment(index: number): void {
    this.showDetailsAssignment[index] = !this.showDetailsAssignment[index];
  }

  toggleDetailsScheduling(index: number): void {
    this.showDetailsScheduling[index] = !this.showDetailsScheduling[index];
  }

  onAssignmentActionChange(newAction: string): void {
    this.rowData.assignment.action = newAction;

    if (newAction == this.actionGenerate) {
      this.schedulingActions = [this.actionGenerate, this.actionNone];
      if (this.rowData.scheduling.action == this.actionOpen) {
        this.onSchedulingActionChange(this.actionGenerate);
      }
    } else if (newAction == this.actionOpen) {
      this.schedulingActions = [this.actionGenerate, this.actionOpen, this.actionNone];
      this.rowData.assignment.parameters.assignmentMethod = '';
      this.selectedAssignmentId = null;
    } else if (newAction == this.actionNone) {
      this.schedulingActions = [this.actionNone];
      this.rowData.assignment.parameters.assignmentMethod = '';
      this.onSchedulingActionChange(this.actionNone);
    }
  }

  onSchedulingActionChange(newAction: string): void {
    this.rowData.scheduling.action = newAction;
  }

  saveItem() {
    console.log();

    var canBeSaved = true;

    if (this.rowData.taskset.action == 'open' && this.selectedTasksetId == undefined) {
      window.alert("L'action pour le taskset est 'Open' mais tu n'a pas séléctionné de taskset dans la liste");
      canBeSaved = false;
    } else if (this.rowData.assignment.action == 'open' && this.selectedAssignmentId == undefined) {
      window.alert("L'action pour l'assignment est 'Open' mais tu n'a pas séléctionné d'assignment dans la liste");
      canBeSaved = false;
    } else if (this.rowData.scheduling.action == 'open' && this.selectedSchedulingId == undefined) {
      window.alert("L'action pour le scheduling est 'Open' mais tu n'a pas séléctionné de scheduling dans la liste");
      canBeSaved = false;
    }

    else if (this.rowData.taskset.action == 'generate') {
      if (this.rowData.taskset.parameters.listOfMaxUtilization.length == 0) {
        window.alert("Selectionner au moins une valeur pour 'List Of Max Utilization'");
        canBeSaved = false;
      }

      else if (this.rowData.taskset.parameters.listOfInterferenceFactors.length == 0) {
        window.alert("Selectionner au moins une valeur pour 'List Of Interference Factors'");
        canBeSaved = false;
      }

      else if (this.rowData.taskset.parameters.listOfProbabilityFactors.length == 0) {
        window.alert("Selectionner au moins une valeur pour 'List Of Probability Factors'");
        canBeSaved = false;
      }
    }

    if (!canBeSaved) {
      return;
    }

    if (this.rowData.assignment.action == 'generate') {
      if (this.rowData.assignment.parameters.assignmentMethod == '') {
        window.alert('Selectionner une méthode d\'assignation');
        canBeSaved = false;
      } else if (this.rowData.assignment.parameters.assignmentMethod == 'CITTA' && this.rowData.assignment.parameters.cittaCriteria.length == 0) {
        window.alert('Selectionner au moins un critère Citta');
        canBeSaved = false;
      }
    }

    if (!canBeSaved) {
      return;
    }

    if (this.rowData.scheduling.action == 'generate') {
      if (this.rowData.scheduling.parameters.schedulingAlgorithms.length == 0) {
        window.alert('Selectionner au moins un algorithme de scheduling');
        canBeSaved = false;
      }
    }

    if (!canBeSaved) {
      return;
    }

    if (canBeSaved) {
      if (window.confirm('Are you sure you want to save this item?')) {
        /*this.rowData.quality = this.quality/10
        this.rowData.positivityRating = this.positivityRating/10
        this.rowData.processed = this.processed == 'Yes' ? true : false  */
  
        if (this.rowData.taskset.action == 'open' && this.selectedTasksetId != undefined) {
          this.rowData.taskset.tasksetId = this.selectedTasksetId;
        }
  
        if (this.rowData.assignment.action == 'open' && this.selectedAssignmentId != undefined) {
          this.rowData.assignment.assignmentId = this.selectedAssignmentId;
          this.rowData.assignment.tasksetId = this.selectedTasksetId;
        }
  
        if (this.rowData.scheduling.action == 'open' && this.selectedSchedulingId != undefined) {
          this.rowData.scheduling.schedulingId = this.selectedSchedulingId;
          this.rowData.scheduling.assignmentId = this.selectedAssignmentId;
          this.rowData.scheduling.tasksetId = this.selectedTasksetId;
        }
  
        if (this.rowData.taskset.action == 'generate') {
          this.rowData.taskset.parameters.listOfMaxUtilization.sort((a, b) => a - b);
          this.rowData.taskset.parameters.listOfProbabilityFactors.sort((a, b) => a - b);
          this.rowData.taskset.parameters.listOfInterferenceFactors.sort((a, b) => a - b);
        }
  
        this.onSave.emit();
        this.onCancel.emit();
      }
    }
  }

  cancel() {
    this.onCancel.emit();
  }
}
