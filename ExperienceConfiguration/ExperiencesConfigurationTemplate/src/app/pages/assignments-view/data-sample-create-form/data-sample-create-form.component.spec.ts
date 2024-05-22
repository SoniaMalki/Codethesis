import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataSampleCreateFormComponent } from './data-sample-create-form.component';

describe('DataSampleCreateFormComponent', () => {
  let component: DataSampleCreateFormComponent;
  let fixture: ComponentFixture<DataSampleCreateFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DataSampleCreateFormComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DataSampleCreateFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
