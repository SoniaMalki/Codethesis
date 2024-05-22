package com.bezkoder.spring.jpa.postgresql.service.llmdata;

import com.bezkoder.spring.jpa.postgresql.model.llmdata.*;
import com.bezkoder.spring.jpa.postgresql.repository.llmdata.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import jakarta.persistence.EntityManager;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class JsonGenerationService {


  @Autowired
  private TasksetRepository tasksetRepository;

  @Autowired
  private TasksetParametersRepository tasksetParametersRepository;

  @Autowired
  private AssignmentRepository assignmentRepository;

  @Autowired
  private AssignmentParametersRepository assignmentParametersRepository;

  @Autowired
  private SchedulingRepository schedulingRepository;

  @Autowired
  private SchedulingParametersRepository schedulingParametersRepository;

  @Autowired
  private ExperienceRepository experienceRepository;

  private final String tasksetFilename = "taskset_";
  private final String assignmentFilename = "assignment_";
  private final String schedulingFilename = "scheduling_";

  public void generateJson() throws IOException {
    List<Experience> allExperiences = experienceRepository.findAll();
    ObjectMapper mapper = new ObjectMapper();
    mapper.enable(SerializationFeature.INDENT_OUTPUT);

    Map<Long, Map<String, Object>> experiencesJsonMap = allExperiences.stream()
      .collect(Collectors.toMap(
        Experience::getId, // Key by Experience ID
        this::transformExperienceToJson, // Map each experience to its JSON representation
        (existing, replacement) -> existing, // In case of key collision, keep the existing value
        HashMap::new // Use a HashMap as the Map implementation
      ));

    // Serialize the map to JSON
    File file = new File("experiences.json");
    mapper.writeValue(file, experiencesJsonMap);
  }

  private Map<String, Object> transformExperienceToJson(Experience experience) {
    Map<String, Object> jsonMap = new HashMap<>();
    jsonMap.put("taskset", mapTaskset(experience.getTaskset()));
    jsonMap.put("assignment", mapAssignment(experience.getAssignment()));
    jsonMap.put("scheduling", mapScheduling(experience.getScheduling()));
    return jsonMap;
  }

  private Map<String, Object> mapTaskset(Taskset taskset) {
    Map<String, Object> map = new HashMap<>();
    map.put("action", taskset.getAction());
    if (taskset.getParameters() == null) {
      taskset.setParameters(tasksetParametersRepository.findById(taskset.getTasksetId()).orElse(null));
    }
    map.put("parameters", taskset.getParameters() != null ? mapTasksetParameters(taskset.getParameters()) : null);
    String tasksetId = taskset.getTasksetId() != null ? taskset.getTasksetId().toString() : "";
    map.put("taskset_id", tasksetFilename + tasksetId);
    return map;
  }

  private Map<String, Object> mapTasksetParameters(TasksetParameters params) {
    Map<String, Object> map = new HashMap<>();
    map.put("number_of_cores", params.getNumberOfCores());
    map.put("list_of_max_utilization", params.getListOfMaxUtilization());
    map.put("list_of_tasks_per_taskset", params.getListOfTasksPerTaskset());
    map.put("taskset_count", params.getTasksetCount());
    map.put("list_of_interference_factors", params.getListOfInterferenceFactors());
    map.put("list_of_probability_factors", params.getListOfProbabilityFactors());
    map.put("min_period", params.getMinPeriod());
    map.put("max_period", params.getMaxPeriod());
    map.put("list_of_period_generation_methods", params.getListOfPeriodGenerationMethods());
    map.put("granularity", params.getGranularity());
    return map;
  }

  private Map<String, Object> mapAssignment(Assignment assignment) {
    Map<String, Object> map = new HashMap<>();
    map.put("action", assignment.getAction());
    if (assignment.getParameters() == null) {
      assignment.setParameters(assignmentParametersRepository.findById(assignment.getAssignmentId()).orElse(null));
    }
    map.put("parameters", assignment.getParameters() != null ? mapAssignmentParameters(assignment.getParameters()) : null);
    String tasksetId = assignment.getTasksetId() != null ? assignment.getTasksetId().toString() : "";
    String assignmentId = assignment.getAssignmentId() != null ? assignment.getAssignmentId().toString() : "";
    map.put("taskset_id", tasksetFilename + tasksetId);
    map.put("assignment_id", assignmentFilename + assignmentId);
    return map;
  }

  private Map<String, Object> mapAssignmentParameters(AssignmentParameters params) {
    Map<String, Object> map = new HashMap<>();
    map.put("assignment_method", params.getAssignmentMethod());
    map.put("citta_criteria", params.getCittaCriteria());
    return map;
  }

  private Map<String, Object> mapScheduling(Scheduling scheduling) {
    Map<String, Object> map = new HashMap<>();
    map.put("action", scheduling.getAction());
    if (scheduling.getParameters() == null) {
      scheduling.setParameters(schedulingParametersRepository.findById(scheduling.getSchedulingId()).orElse(null));
    }
    map.put("parameters", scheduling.getParameters() != null ? mapSchedulingParameters(scheduling.getParameters()) : null);
    String tasksetId = scheduling.getTasksetId() != null ? scheduling.getTasksetId().toString() : "";
    String assignmentId = scheduling.getAssignmentId() != null ? scheduling.getAssignmentId().toString() : "";
    String schedulingId = scheduling.getSchedulingId() != null ? scheduling.getSchedulingId().toString() : "";
    map.put("taskset_id", tasksetFilename + tasksetId);
    map.put("assignment_id", assignmentFilename + assignmentId);
    map.put("scheduling_id", schedulingFilename + schedulingId);
    return map;
  }

  private Map<String, Object> mapSchedulingParameters(SchedulingParameters params) {
    Map<String, Object> map = new HashMap<>();
    map.put("scheduling_algorithms", params.getSchedulingAlgorithms());
    return map;
  }
}
