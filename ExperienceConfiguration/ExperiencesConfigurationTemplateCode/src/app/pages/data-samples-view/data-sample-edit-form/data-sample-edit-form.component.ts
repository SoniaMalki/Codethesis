import { Component, EventEmitter, Input, Output, OnInit, TemplateRef } from '@angular/core';
import { NbDialogService } from '@nebular/theme';

@Component({
  selector: 'ngx-data-sample-edit-form',
  templateUrl: './data-sample-edit-form.component.html',
  styleUrls: ['./data-sample-edit-form.component.scss']
})
export class DataSampleEditFormComponent implements OnInit {
  @Output() onSave = new EventEmitter<void>();
  @Output() onCancel = new EventEmitter<void>();
  @Input() rowData: any;

  actionGenerate = 'generate';
  actionOpen = 'open';
  actionNone = 'none';

  tasksetActions: string[];
  assignmentActions: string[];
  schedulingActions: string[];

  numberOfCores = Array.from({ length: 20 }, (_, i) => i + 1);
  listOfMaxUtilizations = Array.from({ length: 10 }, (_, i) => this.formatNumber((i + 1) * 0.1));
  listOfTaskPerTaskset = Array.from({ length: 20 }, (_, i) => i + 1);
  tasksetCount = Array.from({ length: 20 }, (_, i) => i + 1);
  listOfInterferenceFactors = Array.from({ length: 6 }, (_, i) => this.formatNumber(i * 0.2));
  listOfPeriodGenerationMethods = ['unif', 'logunif', 'prime_matrix'];

  assignmentMethods = ['citta', 'ffdu'];
  cittaCriterias = ['et', 'big'];

  schedulingAlgorithms = ['edf', 'dm'];

  constructor(private dialogService: NbDialogService) {}

  ngOnInit() {
    this.initializeForm();
  }

  initializeForm() {
    this.tasksetActions = [this.actionGenerate, this.actionOpen];
    this.assignmentActions = [this.actionGenerate, this.actionOpen, this.actionNone];
    this.schedulingActions = [this.actionGenerate, this.actionOpen, this.actionNone];

    if (this.rowData && this.rowData.taskset.action === this.actionGenerate) {
      this.assignmentActions = [this.actionGenerate, this.actionNone];
      this.schedulingActions = [this.actionGenerate, this.actionNone];
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

    if (newAction === this.actionGenerate) {
      this.assignmentActions = [this.actionGenerate, this.actionNone];
      this.schedulingActions = [this.actionGenerate, this.actionNone];

      if (this.rowData.assignment.action === this.actionOpen) {
        this.rowData.assignment.action = this.actionGenerate;
      }

      if (this.rowData.scheduling.action === this.actionOpen) {
        this.rowData.scheduling.action = this.actionGenerate;
      }
    } else if (newAction === this.actionOpen) {
      this.assignmentActions = [this.actionOpen, this.actionNone];
      this.schedulingActions = [this.actionOpen, this.actionNone];

      if (this.rowData.assignment.action === this.actionGenerate) {
        this.rowData.assignment.action = this.actionOpen;
      }

      if (this.rowData.scheduling.action === this.actionGenerate) {
        this.rowData.scheduling.action = this.actionOpen;
      }
    }
  }

  onAssignmentActionChange(newAction: string): void {
    this.rowData.assignment.action = newAction;

    if (newAction === this.actionGenerate) {
      this.schedulingActions = [this.actionGenerate, this.actionNone];

      if (this.rowData.scheduling.action === this.actionOpen) {
        this.rowData.scheduling.action = this.actionGenerate;
      }
    } else if (newAction === this.actionOpen) {
      this.schedulingActions = [this.actionOpen, this.actionNone];
      this.rowData.assignment.parameters.assignmentMethod = [];
    } else if (newAction === this.actionNone) {
      this.schedulingActions = [this.actionNone];
      this.rowData.assignment.parameters.assignmentMethod = [];
      this.rowData.scheduling.action = this.actionNone;
    }
  }

  onSchedulingActionChange(newValue: string): void {
    this.rowData.scheduling.action = newValue;
    console.log('Action changed to:', newValue);
  }

  saveItem() {
    let canBeSaved = true;
    
    // Taskset validations
    if (this.rowData.taskset.action === 'open' && !this.rowData.taskset.tasksetId) {
      window.alert("L'action pour le taskset est 'Open' mais tu n'as pas sélectionné de taskset dans la liste");
      canBeSaved = false;
    } else if (this.rowData.taskset.action === 'generate') {
      if (this.rowData.taskset.parameters.numberOfCores = "") {
        window.alert("Sélectionner une valeur pour 'Nbr of cores'");
        canBeSaved = false;
      } else if (this.rowData.taskset.parameters.tasksetCount = "") {
        window.alert("Sélectionner une valeur pour 'Taskset count'");
        canBeSaved = false;
      } else if (this.rowData.taskset.parameters.listOfTasksPerTaskset = "") {
        window.alert("Sélectionner une valeur pour 'Task per taskset'");
        canBeSaved = false;
      } else if (!this.rowData.taskset.parameters.listOfMaxUtilization.length) {
        window.alert("Sélectionner au moins une valeur pour 'Max utilizations'");
        canBeSaved = false;
      } else if (!this.rowData.taskset.parameters.listOfInterferenceFactors.length) {
        window.alert("Sélectionner au moins une valeur pour 'Interference factors'");
        canBeSaved = false;
      } else if (!this.rowData.taskset.parameters.listOfProbabilityFactors.length) {
        window.alert("Sélectionner au moins une valeur pour 'Probability factors'");
        canBeSaved = false;
      }
    }

    // Assignment validations
    if (this.rowData.assignment.action === 'open' && !this.rowData.assignment.assignmentId) {
      window.alert("L'action pour l'assignment est 'Open' mais tu n'as pas sélectionné d'assignment dans la liste");
      canBeSaved = false;
    } else if (this.rowData.assignment.action === 'generate') {
      if (!this.rowData.assignment.parameters.assignmentMethod.length) {
        window.alert("Sélectionner une méthode d'assignation");
        canBeSaved = false;
      } else if (this.rowData.assignment.parameters.assignmentMethod.includes('citta') && !this.rowData.assignment.parameters.cittaCriteria.length) {
        window.alert('Sélectionner au moins un critère Citta');
        canBeSaved = false;
      }
    }

    // Scheduling validations
    if (this.rowData.scheduling.action === 'open' && !this.rowData.scheduling.schedulingId) {
      window.alert("L'action pour le scheduling est 'Open' mais tu n'as pas sélectionné de scheduling dans la liste");
      canBeSaved = false;
    } else if (this.rowData.scheduling.action === 'generate' && !this.rowData.scheduling.parameters.schedulingAlgorithms.length) {
      window.alert('Sélectionner au moins un algorithme de scheduling');
      canBeSaved = false;
    }

    if (!canBeSaved) {
      return;
    }

    if (window.confirm('Are you sure you want to save this item?')) {
      if (this.rowData.taskset.action === 'open' && this.rowData.taskset.tasksetId) {
        this.rowData.taskset.tasksetId = this.rowData.taskset.tasksetId;
      }

      if (this.rowData.assignment.action === 'open' && this.rowData.assignment.assignmentId) {
        this.rowData.assignment.assignmentId = this.rowData.assignment.assignmentId;
        this.rowData.assignment.tasksetId = this.rowData.taskset.tasksetId;
      }

      if (this.rowData.scheduling.action === 'open' && this.rowData.scheduling.schedulingId) {
        this.rowData.scheduling.schedulingId = this.rowData.scheduling.schedulingId;
        this.rowData.scheduling.assignmentId = this.rowData.assignment.assignmentId;
        this.rowData.scheduling.tasksetId = this.rowData.taskset.tasksetId;
      }

      if (this.rowData.taskset.action === 'generate') {
        this.rowData.taskset.parameters.listOfMaxUtilization.sort((a, b) => a - b);
        this.rowData.taskset.parameters.listOfProbabilityFactors.sort((a, b) => a - b);
        this.rowData.taskset.parameters.listOfInterferenceFactors.sort((a, b) => a - b);
      }

      this.onSave.emit();
      this.onCancel.emit();
    }
  }

  cancel() {
    this.onCancel.emit();
  }
}
