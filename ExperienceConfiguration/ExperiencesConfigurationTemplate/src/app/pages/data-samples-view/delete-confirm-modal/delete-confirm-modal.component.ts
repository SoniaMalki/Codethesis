import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'ngx-delete-confirm-modal',
  templateUrl: './delete-confirm-modal.component.html',
  styleUrls: ['./delete-confirm-modal.component.scss']
})
export class DeleteConfirmModalComponent {

  @Output() onDelete = new EventEmitter<void>();
  @Output() onCancel = new EventEmitter<void>();

  @Input() title: string; 

  delete() {
    this.onDelete.emit();
    this.onCancel.emit();
  }

  cancel() {
    this.onCancel.emit();
  }
}
