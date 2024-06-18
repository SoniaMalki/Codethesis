export interface DataSamplesFilters {
  minQuality?: number;
  maxQuality?: number;
  minPositivityRating?: number;
  maxPositivityRating?: number;
  processed?: boolean;
  deleted?: boolean;
  sources?: string[]; 
  references?: string[]; 
  tags?: string[];
}