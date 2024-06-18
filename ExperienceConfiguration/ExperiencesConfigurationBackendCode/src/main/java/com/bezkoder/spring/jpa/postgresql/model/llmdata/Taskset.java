package com.bezkoder.spring.jpa.postgresql.model.llmdata;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import lombok.Data;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;


@Entity
@Data
public class Taskset {
  @Id
  @GeneratedValue(strategy = GenerationType.AUTO)
  private Long id;

  private String action;

  @OneToOne(cascade = CascadeType.ALL)
  @JoinColumn(name = "parameters_id", referencedColumnName = "id")
  private TasksetParameters parameters;

  private Long tasksetId;
}
