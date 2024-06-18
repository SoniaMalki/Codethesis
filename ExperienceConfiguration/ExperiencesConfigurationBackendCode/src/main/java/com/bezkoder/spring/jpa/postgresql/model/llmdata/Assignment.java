package com.bezkoder.spring.jpa.postgresql.model.llmdata;

import jakarta.persistence.*;
import lombok.Data;


@Entity
@Data
public class Assignment {
  @Id
  @GeneratedValue(strategy = GenerationType.AUTO)
  private Long id;

  private String action;

  @OneToOne(cascade = CascadeType.ALL)
  @JoinColumn(name = "parameters_id", referencedColumnName = "id")
  private AssignmentParameters parameters;

  private Long tasksetId;

  private Long assignmentId;
}
