import { TestBed } from '@angular/core/testing';

import { DataSampleService } from './datasample.service';

describe('DatasampleService', () => {
  let service: DataSampleService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DataSampleService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
