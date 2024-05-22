import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataSampleFileIconComponent } from './data-sample-edit-icon-component';

describe('DataSampleEditIconComponentComponent', () => {
  let component: DataSampleFileIconComponent;
  let fixture: ComponentFixture<DataSampleFileIconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DataSampleFileIconComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DataSampleFileIconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
