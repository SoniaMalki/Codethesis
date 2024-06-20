package com.bezkoder.spring.jpa.postgresql.model.llmdata;

import jakarta.persistence.*;
import lombok.Data;

import java.util.List;


@Entity
@Data
public class TasksetParameters {
  @Id
  @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "tasksetparameters_generator")
  @SequenceGenerator(name = "tasksetparameters_generator", sequenceName = "tasksetparameters_seq", allocationSize = 1)
  private Long id;

  private Integer numberOfCores;

  @ElementCollection
  private List<Double> listOfMaxUtilization;

  private Integer listOfTasksPerTaskset;

  private Integer tasksetCount;

  @ElementCollection
  private List<Double> listOfInterferenceFactors;

  @ElementCollection
  private List<Double> listOfProbabilityFactors;


  @ElementCollection
  private List<Double> granularity;
}
