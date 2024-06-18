package com.bezkoder.spring.jpa.postgresql.model.llmdata;

import jakarta.persistence.*;
import lombok.Data;
import lombok.ToString;

@Entity
@Data
@ToString
public class Scheduling {
  @Id
  @GeneratedValue(strategy = GenerationType.AUTO)
  private Long id;

  private String action;

  @OneToOne(cascade = CascadeType.ALL)
  @JoinColumn(name = "parameters_id", referencedColumnName = "id")
  private SchedulingParameters parameters;

  private Long tasksetId;

  private Long assignmentId;

  private Long schedulingId;
}
