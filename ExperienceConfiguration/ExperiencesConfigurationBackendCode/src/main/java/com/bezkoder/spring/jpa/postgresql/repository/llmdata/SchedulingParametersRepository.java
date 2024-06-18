package com.bezkoder.spring.jpa.postgresql.repository.llmdata;

import com.bezkoder.spring.jpa.postgresql.model.llmdata.SchedulingParameters;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface SchedulingParametersRepository extends JpaRepository<SchedulingParameters, Long>, JpaSpecificationExecutor<SchedulingParameters> {
}
