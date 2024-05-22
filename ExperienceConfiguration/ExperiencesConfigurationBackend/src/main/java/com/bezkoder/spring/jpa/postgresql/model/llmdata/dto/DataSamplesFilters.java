package com.bezkoder.spring.jpa.postgresql.model.llmdata.dto;

import lombok.Data;

import java.util.List;

@Data
public class DataSamplesFilters {
  private Double minQuality;
  private Double maxQuality;
  private Double minPositivityRating;
  private Double maxPositivityRating;
  private Boolean processed;
  private Boolean deleted;
  private String source;
  private List<String> sources;
  private List<String> references;
  private List<String> tags;
}

