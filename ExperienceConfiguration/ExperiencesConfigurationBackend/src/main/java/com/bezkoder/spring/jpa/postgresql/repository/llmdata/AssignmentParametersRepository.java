package com.bezkoder.spring.jpa.postgresql.repository.llmdata;

import com.bezkoder.spring.jpa.postgresql.model.llmdata.AssignmentParameters;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface AssignmentParametersRepository extends JpaRepository<AssignmentParameters, Long>, JpaSpecificationExecutor<AssignmentParameters> {
}
