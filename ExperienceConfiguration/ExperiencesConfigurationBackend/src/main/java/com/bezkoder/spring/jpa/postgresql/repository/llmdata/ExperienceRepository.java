package com.bezkoder.spring.jpa.postgresql.repository.llmdata;

import com.bezkoder.spring.jpa.postgresql.model.llmdata.Experience;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface ExperienceRepository extends JpaRepository<Experience, Long>, JpaSpecificationExecutor<Experience> {
}
