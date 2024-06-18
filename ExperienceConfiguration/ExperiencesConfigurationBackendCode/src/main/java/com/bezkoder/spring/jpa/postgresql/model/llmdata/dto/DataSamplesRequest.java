package com.bezkoder.spring.jpa.postgresql.model.llmdata.dto;

import lombok.Data;

@Data
public class DataSamplesRequest {
  private DataSamplesFilters filters;
  private String sortBy;
  private String sortOrder;
}
