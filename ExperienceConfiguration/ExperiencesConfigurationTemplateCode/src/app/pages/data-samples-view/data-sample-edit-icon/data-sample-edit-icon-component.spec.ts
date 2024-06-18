import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataSampleEditIconComponent } from './data-sample-edit-icon-component';

describe('DataSampleEditIconComponentComponent', () => {
  let component: DataSampleEditIconComponent;
  let fixture: ComponentFixture<DataSampleEditIconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DataSampleEditIconComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DataSampleEditIconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
