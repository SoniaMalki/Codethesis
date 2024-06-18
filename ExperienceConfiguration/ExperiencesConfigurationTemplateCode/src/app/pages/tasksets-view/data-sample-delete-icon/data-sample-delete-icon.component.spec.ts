import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataSampleDeleteIconComponent } from './data-sample-delete-icon.component';

describe('DataSampleDeleteIconComponent', () => {
  let component: DataSampleDeleteIconComponent;
  let fixture: ComponentFixture<DataSampleDeleteIconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DataSampleDeleteIconComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DataSampleDeleteIconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
