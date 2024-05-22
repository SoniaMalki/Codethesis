import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClickableIconComponent } from './clickable-icon.component';

describe('ClickableComponentComponent', () => {
  let component: ClickableIconComponent;
  let fixture: ComponentFixture<ClickableIconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ClickableIconComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ClickableIconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
