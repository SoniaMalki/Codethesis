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

  selectedSources: string[] = [];
  selectedReferences: string[] = [];
  selectedTags: string[] = [];

  selectedProcessedValue : boolean = false;
  selectedDeletedValue : boolean = false;
  dataList : any[] = []
  sources: string[];
  references: string[];
  tags: string[];

  createRowData: any;

  sortByOptions = ['createdDate', 'updatedDate', 'quality', 'positivityRating', 'source', 'reference'];
  sortOrderOptions = ['asc', 'desc'];

  sortBy: string = 'createdDate';  
  sortOrder: string = 'asc';       


  constructor(public dataSampleService: DataSampleService, private dialogService: NbDialogService, private toastrService: NbToastrService) {
      this.fetchEnumData()

      this.selectedSources = this.sources
      this.selectedReferences = this.references
      this.selectedTags = this.tags == undefined ? [] : this.tags
  }

  private fetchDataSamples(): void {
    console.log("EXAMPLE YES")
    console.log(this.selectedTags)
    const filters: DataSamplesFilters = {
      minQuality: 0,
      maxQuality: 1,
      minPositivityRating: 0,
      maxPositivityRating: 1,
      processed: this.selectedProcessedValue,
      deleted: this.selectedDeletedValue,
      sources: this.selectedSources.length > 0 ? this.selectedSources : undefined,
      references: this.selectedReferences.length > 0 ? this.selectedReferences : undefined,
      tags: this.selectedTags.length > 0 ? this.selectedTags : undefined
    };
    console.log("EXAMPLES YES")
    const request: DataSamplesRequest = { 
      filters,
      sortBy: this.sortBy,
      sortOrder: this.sortOrder 
    };
    console.log("EXAMPLES EXAMPLES YES")
    this.dataSampleService.getDataSamples(request).subscribe(
      (data: any) => {
        this.dataList = data;
        console.log(data);
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  fetchEnumData() {
    this.dataSampleService.getDataSampleEnums().subscribe({
      next: (enums) => {
        this.sources = enums.sources;
        this.references = enums.references.map(ref => ref.toString());
        this.tags = enums.tags;

        this.selectedSources = [...this.sources];
        this.selectedReferences = [...this.references];

        console.log(this.sources)
        console.log(this.references)
        console.log(this.tags)

        this.fetchDataSamples()
      },
      error: (err) => console.error('Failed to load enum data:', err)
    });
  }

  onFieldChanged(): void {
    console.log("example")
    this.fetchDataSamples()
  }



  onEditButtonClicked(rowData: any) {
    console.log('Edit data:', rowData);
    this.openEditModal(rowData)
  }

  openCreateModal() {
    this.createRowData = {
      positivityRating: 0.5,
      quality: 0.5,
      reference: "Undefined",
      source: "Discord",
      tags: ["CreatedInInterface"],
      instruction: "",
      input: "",
      output: "",
      additionalInfo: "",
      fr_instruction: "",
      fr_input: "",
      fr_output: "",
      fr_additional_info: "",
      processed: false
    }

    let dialogRef = this.dialogService.open(DataSampleCreateFormComponent, {
      context: {
        rowData: this.createRowData,
        sources: this.sources,
        references: this.references,
        tags: this.tags
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
    let dialogRef = this.dialogService.open(DataSampleEditFormComponent, {
      context: {
        rowData: rowData,
        sources: this.sources,
        references: this.references,
        tags: this.tags
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
        title: rowData.output ? rowData.output : (rowData.fr_output ? rowData.fr_output : 'No data')  // Ensure this is being passed correctly
      }});

    dialogRef.onClose.subscribe(result => {
      // Handle dialog close with result
    });

    const subSoftDelete = dialogRef.componentRef.instance.onSoftDelete.subscribe(() => {
      this.handleSoftDelete(rowData);
    });

    const subDelete = dialogRef.componentRef.instance.onDelete.subscribe(() => {
      this.handleDelete(rowData);
    });

    const subCancel = dialogRef.componentRef.instance.onCancel.subscribe(() => {
      dialogRef.close();
    });

    dialogRef.onClose.subscribe(() => {
      // Cleanup subscriptions when the dialog is closed
      subSoftDelete.unsubscribe();
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
    this.dataSampleService.createDataSample(rowData).subscribe({
      next: (response) => {
        console.log('Create success:', response);
        this.showToast('success', 'Data sample created successfully', '');
        this.fetchDataSamples(); 
      },
      error: (err) => {
        console.error('Error during create:', err);
        this.showToast('danger', 'Error while trying to create data sample', '');
        this.fetchDataSamples(); 
      }
    });
  }

  handleSave(rowData: any) {
    console.log('Save:', rowData);
    this.dataSampleService.updateDataSample(rowData.id, rowData).subscribe({
      next: (response) => {
        console.log('Update success:', response);
        this.showToast('success', 'Data sample updated successfully', '');
        this.fetchDataSamples(); 
      },
      error: (err) => {
        console.error('Error during update:', err);
        this.showToast('danger', 'Error while trying to update data sample', '');
        this.fetchDataSamples(); 
      }
    });
  }

  handleSoftDelete(rowData: any) {
    console.log('Soft delete:', rowData);
    this.dataSampleService.softDeleteDataSample(rowData.id).subscribe({
      next: (response) => { console.log(response); this.showToast('success', 'Successfully soft deleted', ''); this.fetchDataSamples() },
      error: (err) => { console.error('Error during soft delete:', err); ; this.showToast('danger', 'Error while trying to soft delete', ''); this.fetchDataSamples() }
    });
    
  }

  handleDelete(rowData: any) {
    console.log('Delete:', rowData);
    this.dataSampleService.deleteDataSample(rowData.id).subscribe({
      next: (response) => { console.log(response); this.showToast('success', 'Successfully deleted', ''); this.fetchDataSamples() },
      error: (err) => { console.error('Error during delete:', err); ; this.showToast('danger', 'Error while trying to delete', ''); this.fetchDataSamples() }
    });
    
  }
}
