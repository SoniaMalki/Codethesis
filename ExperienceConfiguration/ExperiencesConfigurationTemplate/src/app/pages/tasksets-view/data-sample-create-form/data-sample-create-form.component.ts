import { Component, EventEmitter, Input, Output, OnInit, TemplateRef  } from '@angular/core';
import { NbDialogService } from '@nebular/theme';
import { Observable } from 'rxjs';

@Component({
  selector: 'ngx-data-sample-create-form',
  templateUrl: './data-sample-create-form.component.html',
  styleUrls: ['./data-sample-create-form.component.scss']
})
export class DataSampleCreateFormComponent {
  @Output() onSave = new EventEmitter<void>();
  @Output() onCancel = new EventEmitter<void>();

  @Input() rowData: any;

  @Input() sources: string[];
  @Input() references: string[];
  @Input() tags: string[];

  translationResultInstruction: string;
  translationResultInput: string;
  translationResultOutput: string;
  translationResultAdditionalInfo: string;
  
  constructor(private dialogService: NbDialogService) {}

  selectedTags = [];
  qualities = Array.from({length: 10}, (_, i) => i + 1); // Creates an array [1, 2, ..., 10]
  positivityRatings = Array.from({length: 10}, (_, i) => i + 1);
  processedValues = ["Yes", "No"];
  processed: string = "No";

  // Ensure these properties match those used in your template
  source: string;
  reference: string;
  quality: number;
  positivityRating: number;
  isExpanded: boolean = false;
  showDeepL: boolean = false;

  toggleTag(tag: string) {
    const index = this.selectedTags.indexOf(tag);
    if (index >= 0) {
      this.selectedTags.splice(index, 1);
    } else {
      this.selectedTags.push(tag);
    }
  }


  ngOnInit() {
    // Initialize model from rowData on input change
    this.initializeForm();
  }

  initializeForm() {
    if (this.rowData) {
      this.source = this.rowData.source;
      this.reference = this.rowData.reference || 'Unset'; // Handle null values
      this.quality = Math.ceil(this.rowData.quality * 10); // Assuming quality is between 0 and 1
      this.positivityRating = this.rowData.positivityRating * 10; // Scale similarly
      this.processed = this.rowData.processed ? "Yes" : "No";
      this.selectedTags = this.rowData.tags || [];
    }
  }



  saveItem() {
  	if (window.confirm("Are you sure you want to save this item?")) {
  	  this.rowData.quality = this.quality/10
  	  this.rowData.positivityRating = this.positivityRating/10
  	  this.rowData.processed = this.processed == 'Yes' ? true : false  
      this.onSave.emit();
      this.onCancel.emit();
    }
  }

  cancel() {
    this.onCancel.emit();
  }
}



