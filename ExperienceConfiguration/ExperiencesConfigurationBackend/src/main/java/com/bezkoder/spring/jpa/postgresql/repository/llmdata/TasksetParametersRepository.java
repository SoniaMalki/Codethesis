package com.bezkoder.spring.jpa.postgresql.repository.llmdata;

import com.bezkoder.spring.jpa.postgresql.model.llmdata.TasksetParameters;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface TasksetParametersRepository extends JpaRepository<TasksetParameters, Long>, JpaSpecificationExecutor<TasksetParameters> {
}
