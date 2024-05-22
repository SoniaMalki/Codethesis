package com.bezkoder.spring.jpa.postgresql.model.llmdata;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;


@Entity
@Table(name = "experiences")
@lombok.Data
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
@EntityListeners(AuditingEntityListener.class)
public class Experience {
  @Id
  @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "experience_generator")
  @SequenceGenerator(name = "experience_generator", sequenceName = "experience_seq", allocationSize = 1)
  private Long id;

  @OneToOne(cascade = CascadeType.ALL)
  @JoinColumn(name = "taskset_id", referencedColumnName = "id")
  private Taskset taskset;

  @OneToOne(cascade = CascadeType.ALL)
  @JoinColumn(name = "assignment_id", referencedColumnName = "id")
  private Assignment assignment;

  @OneToOne(cascade = CascadeType.ALL)
  @JoinColumn(name = "scheduling_id", referencedColumnName = "id")
  private Scheduling scheduling;

  // Getters et Setters
}
