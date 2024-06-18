import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'ngx-delete-confirm-modal',
  templateUrl: './delete-confirm-modal.component.html',
  styleUrls: ['./delete-confirm-modal.component.scss']
})
export class DeleteConfirmModalComponent {

  @Output() onSoftDelete = new EventEmitter<void>();
  @Output() onDelete = new EventEmitter<void>();
  @Output() onCancel = new EventEmitter<void>();

  @Input() title: string; 


  softDelete() {
    this.onSoftDelete.emit();
    this.onCancel.emit();
  }

  delete() {
  	if (window.confirm("Are you sure you want to permanently delete this item?")) {
      this.onDelete.emit();
      this.onCancel.emit();
    }
  }

  cancel() {
    this.onCancel.emit();
  }
}
