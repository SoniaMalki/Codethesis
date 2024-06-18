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

  @Input() sources: string[];
  @Input() references: string[];
  @Input() tags: string[];

  translationResultInstruction: string;
  translationResultInput: string;
  translationResultOutput: string;
  translationResultAdditionalInfo: string;
  
  constructor(private http: HttpClient, private dialogService: NbDialogService) {}

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


  translateInstructionToFrench() {
    this.translateToFrench(this.rowData.instruction).subscribe((result) => {
      this.translationResultInstruction = result;
    });
  }

  translateInputToFrench() {
    this.translateToFrench(this.rowData.input).subscribe((result) => {
      this.translationResultInput = result;
    });
  }

  translateOutputToFrench() {
    this.translateToFrench(this.rowData.output).subscribe((result) => {
      this.translationResultOutput = result;
    });
  }

  translateAdditionalInfoToFrench() {
    this.translateToFrench(this.rowData.additionalInfo).subscribe((result) => {
      this.translationResultAdditionalInfo = result;
    });
  }


  translateToFrench(textToTranslate: string): Observable<string> {
    const apiKey = '0cc79d9f-574b-fc9c-7a64-22ac81771a0d:fx'; // Replace with your DeepL API key
    const apiUrl = `https://api-free.deepl.com/v2/translate?auth_key=${apiKey}&text=${encodeURIComponent(textToTranslate)}&target_lang=FR`;

    return new Observable((observer) => {
      this.http.get(apiUrl).subscribe(
        (response: any) => {
          observer.next(response.translations[0].text);
          observer.complete();
        },
        (error) => {
          console.error('Translation failed:', error);
          observer.error('Translation failed');
        }
      );
    });
  }


  expand() {
    if (this.isExpanded) {
      // Reset the state when closing
      this.isExpanded = false;
      this.showDeepL = false;
    } else {
      this.isExpanded = true;
      setTimeout(() => (this.showDeepL = true), 300); // Adjust the delay as needed
    }
  }

  openDialog(dialog: TemplateRef<any>) {
    this.dialogService.open(dialog, {
      context: 'French Translation Result',
    });
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



