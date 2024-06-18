import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataSampleEditFormComponent } from './data-sample-edit-form.component';

describe('DataSampleEditFormComponent', () => {
  let component: DataSampleEditFormComponent;
  let fixture: ComponentFixture<DataSampleEditFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DataSampleEditFormComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DataSampleEditFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
