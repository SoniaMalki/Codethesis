package com.bezkoder.spring.jpa.postgresql.model.llmdata;

import jakarta.persistence.*;
import lombok.Data;

import java.util.List;

@Entity
@Data
public class SchedulingParameters {
  @Id
  @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "schedulingparameters_generator")
  @SequenceGenerator(name = "schedulingparameters_generator", sequenceName = "schedulingparameters_seq", allocationSize = 1)
  private Long id;

  @ElementCollection
  private List<String> schedulingAlgorithms;
}
