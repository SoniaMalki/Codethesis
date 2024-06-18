package com.bezkoder.spring.jpa.postgresql.repository.llmdata;

import com.bezkoder.spring.jpa.postgresql.model.llmdata.Scheduling;
import com.bezkoder.spring.jpa.postgresql.model.llmdata.SchedulingParameters;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

import java.util.List;

public interface SchedulingRepository extends JpaRepository<Scheduling, Long>, JpaSpecificationExecutor<Scheduling> {
  List<Scheduling> findByTasksetIdAndParametersIsNotNull(Long assignmentId);
  List<Scheduling> findByAssignmentIdAndParametersIsNotNull(Long assignmentId);
}
