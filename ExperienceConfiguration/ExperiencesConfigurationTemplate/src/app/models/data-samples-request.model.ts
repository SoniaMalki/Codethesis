import { DataSamplesFilters } from './data-samples-filters.model';

export interface DataSamplesRequest {
  filters: DataSamplesFilters;
  sortBy: string,
  sortOrder: string
}