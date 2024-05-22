import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomTextCellComponent } from './custom-text-cell.component';

describe('CustomTextCellComponent', () => {
  let component: CustomTextCellComponent;
  let fixture: ComponentFixture<CustomTextCellComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CustomTextCellComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CustomTextCellComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
