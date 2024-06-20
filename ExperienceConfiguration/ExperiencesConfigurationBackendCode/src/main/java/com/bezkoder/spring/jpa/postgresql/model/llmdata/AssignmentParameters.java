package com.bezkoder.spring.jpa.postgresql.model.llmdata;

import jakarta.persistence.*;
import lombok.Data;

import java.util.List;

@Entity
@Data
public class AssignmentParameters {
  @Id
  @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "assignmentparameters_generator")
  @SequenceGenerator(name = "assignmentparameters_generator", sequenceName = "assignmentparameters_seq", allocationSize = 1)
  private Long id;

  @ElementCollection
  private List<String> assignmentMethod;

  @ElementCollection
  private List<String> cittaCriteria;
}
