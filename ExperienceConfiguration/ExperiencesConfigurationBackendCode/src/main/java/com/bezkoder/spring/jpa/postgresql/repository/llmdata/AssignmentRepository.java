package com.bezkoder.spring.jpa.postgresql.repository.llmdata;

import com.bezkoder.spring.jpa.postgresql.model.llmdata.Assignment;
import com.bezkoder.spring.jpa.postgresql.model.llmdata.AssignmentParameters;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

import java.util.List;

public interface AssignmentRepository extends JpaRepository<Assignment, Long>, JpaSpecificationExecutor<Assignment> {
  List<Assignment> findByTasksetIdAndParametersIsNotNull(Long tasksetId);
}
