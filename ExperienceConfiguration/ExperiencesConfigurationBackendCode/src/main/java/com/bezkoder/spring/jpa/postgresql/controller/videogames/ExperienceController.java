package com.bezkoder.spring.jpa.postgresql.controller.videogames;

import com.bezkoder.spring.jpa.postgresql.model.llmdata.*;
import com.bezkoder.spring.jpa.postgresql.repository.llmdata.*;
import com.bezkoder.spring.jpa.postgresql.service.llmdata.ExecuteService;
import com.bezkoder.spring.jpa.postgresql.service.llmdata.JsonGenerationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@CrossOrigin(origins = "http://localhost:4200")
@RestController
@RequestMapping("/api/configuration/")
public class ExperienceController {

  @Autowired
  TasksetRepository tasksetRepository;

	@Autowired
  TasksetParametersRepository tasksetParametersRepository;

  @Autowired
  AssignmentRepository assignmentRepository;

  @Autowired
  AssignmentParametersRepository assignmentParametersRepository;

  @Autowired
  SchedulingRepository schedulingRepository;

  @Autowired
  SchedulingParametersRepository schedulingParametersRepository;

  @Autowired
  ExperienceRepository experienceRepository;


  @Autowired
  JsonGenerationService jsonGenerationService;

  @Autowired
  ExecuteService executeService;


  @GetMapping("/tasksets")
  public List<TasksetParameters> getAllTasksets() {
    return tasksetParametersRepository.findAll();
  }
  @GetMapping("/assignments")
  public List<AssignmentParameters> getAllAssignments() {
    return assignmentParametersRepository.findAll();
  }

  @GetMapping("/schedulings")
  public List<SchedulingParameters> getAllSchedulings() {
    return schedulingParametersRepository.findAll();
  }


  @GetMapping("/experiences")
  public List<Experience> getAllExperiences() {
    return experienceRepository.findAll();
  }

  @PostMapping("/experiences")
  public ResponseEntity<Experience> createExperience(@RequestBody Experience newExperience) {
    System.out.println("Received JSON: " + newExperience);
    if(newExperience.getTaskset().getAction().equals("open")) {
      newExperience.getTaskset().setParameters(null);
    }
    if(newExperience.getAssignment().getAction().equals("open")) {;
      newExperience.getAssignment().setParameters(null);
    }
    if(newExperience.getScheduling().getAction().equals("open")) {
      newExperience.getScheduling().setParameters(null);
    }
    Experience savedExperience = experienceRepository.save(newExperience);

    Long tasksetId = savedExperience.getTaskset().getAction().equals("generate") ?  savedExperience.getTaskset().getParameters().getId() : savedExperience.getTaskset().getTasksetId();
    Long assignmentId = savedExperience.getAssignment().getAction().equals("generate") ?  savedExperience.getAssignment().getParameters().getId() : savedExperience.getAssignment().getAssignmentId();
    Long schedulingId = savedExperience.getScheduling().getAction().equals("generate") ?  savedExperience.getScheduling().getParameters().getId() : savedExperience.getScheduling().getSchedulingId();

    if(savedExperience.getTaskset().getAction().equals("generate")) {
      savedExperience.getTaskset().setTasksetId(tasksetId);
      tasksetRepository.save(savedExperience.getTaskset());
    }

    if(savedExperience.getAssignment().getAction().equals("generate")) {
      savedExperience.getAssignment().setTasksetId(tasksetId);
      savedExperience.getAssignment().setAssignmentId(assignmentId);
      assignmentRepository.save(savedExperience.getAssignment());
    }

    if(savedExperience.getScheduling().getAction().equals("generate")) {
      savedExperience.getScheduling().setTasksetId(tasksetId);
      savedExperience.getScheduling().setAssignmentId(assignmentId);
      savedExperience.getScheduling().setSchedulingId(schedulingId);
      schedulingRepository.save(savedExperience.getScheduling());
    }

    try {
      this.jsonGenerationService.generateJson();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    return ResponseEntity.ok(savedExperience);
  }

  @PutMapping("/experiences/{id}")
  public ResponseEntity<?> updateExperience(@PathVariable Long id, @RequestBody Experience updatedExperience) {
    return experienceRepository.findById(id)
      .map(experience -> {
        if(updatedExperience.getTaskset().getAction().equals("open")) {
          updatedExperience.getTaskset().setParameters(null);
        }
        if(updatedExperience.getAssignment().getAction().equals("open")) {
          updatedExperience.getAssignment().setParameters(null);
        }
        if(updatedExperience.getScheduling().getAction().equals("open")) {
          updatedExperience.getScheduling().setParameters(null);
        }
        System.out.println("EXAMPLE");
        Experience savedExperience = experienceRepository.save(updatedExperience);

        System.out.println(savedExperience);

        Long tasksetId = savedExperience.getTaskset().getAction().equals("generate") ?  savedExperience.getTaskset().getParameters().getId() : savedExperience.getTaskset().getTasksetId();
        Long assignmentId = savedExperience.getAssignment().getAction().equals("generate") ?  savedExperience.getAssignment().getParameters().getId() : savedExperience.getAssignment().getAssignmentId();
        Long schedulingId = savedExperience.getScheduling().getAction().equals("generate") ?  savedExperience.getScheduling().getParameters().getId() : savedExperience.getScheduling().getSchedulingId();

        if(savedExperience.getTaskset().getAction().equals("generate")) {
          savedExperience.getTaskset().setTasksetId(tasksetId);
          tasksetRepository.save(savedExperience.getTaskset());
        }

        if(savedExperience.getAssignment().getAction().equals("generate")) {
          savedExperience.getAssignment().setTasksetId(tasksetId);
          savedExperience.getAssignment().setAssignmentId(assignmentId);
          assignmentRepository.save(savedExperience.getAssignment());
        }

        if(savedExperience.getScheduling().getAction().equals("generate")) {
          savedExperience.getScheduling().setTasksetId(tasksetId);
          savedExperience.getScheduling().setAssignmentId(assignmentId);
          savedExperience.getScheduling().setSchedulingId(schedulingId);
          schedulingRepository.save(savedExperience.getScheduling());
        }

        try {
          this.jsonGenerationService.generateJson();
        } catch (IOException e) {
          throw new RuntimeException(e);
        }

        return ResponseEntity.ok(updatedExperience);
      })
      .orElseGet(() -> ResponseEntity.notFound().build());
  }

  // Method to filter AssignmentParameters and related Scheduling by TasksetId
  @GetMapping("/filterByTasksetId/{tasksetId}")
  public ResponseEntity<?> filterByTasksetId(@PathVariable Long tasksetId) {

    System.out.println(String.format("Filter by tasksetId : %s", tasksetId));

    List<Assignment> assignments = assignmentRepository.findByTasksetIdAndParametersIsNotNull(tasksetId);
    List<AssignmentParameters> assignmentParams = assignments.stream()
      .map(Assignment::getParameters)
      .collect(Collectors.toList());

    List<Scheduling> schedulings = schedulingRepository.findByTasksetIdAndParametersIsNotNull(tasksetId);
    List<SchedulingParameters> schedulingParams = schedulings.stream()
      .map(Scheduling::getParameters)
      .collect(Collectors.toList());


    Map<String, Object> result = new HashMap<>();
    result.put("assignmentParameters", assignmentParams);
    result.put("schedulingParameters", schedulingParams);

    return ResponseEntity.ok(result);
  }

  // Method to filter SchedulingParameters by AssignmentId
  @GetMapping("/filterByAssignmentId/{assignmentId}")
  public ResponseEntity<List<SchedulingParameters>> filterByAssignmentId(@PathVariable Long assignmentId) {
    System.out.println(String.format("Filter by assignmentId : %s", assignmentId));
    List<Scheduling> schedulings = schedulingRepository.findByAssignmentIdAndParametersIsNotNull(assignmentId);
    System.out.println(Arrays.toString(schedulings.toArray()));
    List<SchedulingParameters> result = schedulings.stream()
      .map(Scheduling::getParameters)
      .collect(Collectors.toList());
    return ResponseEntity.ok(result);
  }



  @DeleteMapping("/experiences/{id}")
  public ResponseEntity<String> deleteExperience(@PathVariable Long id) {
    return experienceRepository.findById(id)
      .map(experience -> {
        experienceRepository.delete(experience);
        try {
          this.jsonGenerationService.generateJson();
        } catch (IOException e) {
          throw new RuntimeException(e);
        }
        return ResponseEntity.ok("The experience has been deleted successfully.");
      })
      .orElseGet(() -> ResponseEntity.notFound().build());
  }


  @PostMapping("/execute")  // ensure the endpoint matches the Angular call
  public ResponseEntity<String> executeScriptWithNumber(@RequestParam Integer number) {
    System.out.println("Execute script");
    System.out.println(number.toString());
    try {
      executeService.executePythonScript(number.toString());
      return ResponseEntity.ok("Execution successful!");
    } catch (IOException e) {
      System.out.println("Error during script execution: " + e.getMessage());
      return ResponseEntity.internalServerError().body("Error during script execution: " + e.getMessage());
    }
  }

   /*
  @PostMapping("")
  public ResponseEntity<List<ExperienceParameters>> getAllDataSamples(@RequestBody DataSamplesRequest request) {
    Sort sort = getSortDirection(request.getSortBy(), request.getSortOrder());
    Specification<ExperienceParameters> spec = DataSampleSpecifications.withFilters(request.getFilters());
    List<ExperienceParameters> experienceParametersList = dataSampleRepository.findAll(spec, sort);
    return ResponseEntity.ok(experienceParametersList);
  }


  @GetMapping("/enums")
  public Map<String, Object> getAllDataSampleEnums() {
    return Map.of(
      "references", Reference.values(),
      "sources", Source.values(),
      "tags", Tag.values()
    );
  }


  @PostMapping("/addSample")
  public ResponseEntity<ExperienceParameters> createDataSample(@RequestBody ExperienceParameters newExperienceParameters) {
    try {
      // Calculate the total tokens for both English and French instructions
      newExperienceParameters.setTotalTokensEnglish(dataSampleService.getNumberTokenInText(
        newExperienceParameters.getEnglish().getOutput() + "\n\n" + newExperienceParameters.getEnglish().getAdditionalInfo()));
      newExperienceParameters.setTotalTokensFrench(dataSampleService.getNumberTokenInText(
        newExperienceParameters.getFrench().getOutput() + "\n\n" + newExperienceParameters.getFrench().getAdditionalInfo()));

      // Set creation date
      newExperienceParameters.setCreatedDate(new Date());
      newExperienceParameters.setUpdatedDate(new Date());

      if (newExperienceParameters.isProcessed()){
        newExperienceParameters.setProcessedDate(new Date());
      }

      // Save the new data sample
      ExperienceParameters savedExperienceParameters = dataSampleRepository.save(newExperienceParameters);

      return ResponseEntity.ok(savedExperienceParameters);
    } catch (IOException e) {
      throw new RuntimeException("Error calculating tokens", e);
    } catch (InterruptedException e) {
      throw new RuntimeException("Token calculation interrupted", e);
    }
  }



  @PutMapping("/{id}")
  public ResponseEntity<?> updateDataSample(@PathVariable Long id, @RequestBody ExperienceParameters updatedExperienceParameters) {
    return dataSampleRepository.findById(id)
      .map(dataSample -> {
        dataSample.setQuality(updatedExperienceParameters.getQuality());
        dataSample.setPositivityRating(updatedExperienceParameters.getPositivityRating());
        dataSample.setSource(updatedExperienceParameters.getSource());
        dataSample.setReference(updatedExperienceParameters.getReference());
        dataSample.setDeleted(updatedExperienceParameters.isDeleted());

        // Updating embedded objects for localizations
        dataSample.getEnglish().setInstruction(updatedExperienceParameters.getEnglish().getInstruction());
        dataSample.getEnglish().setInput(updatedExperienceParameters.getEnglish().getInput());
        dataSample.getEnglish().setOutput(updatedExperienceParameters.getEnglish().getOutput());
        dataSample.getEnglish().setAdditionalInfo(updatedExperienceParameters.getEnglish().getAdditionalInfo());

        dataSample.getFrench().setInstruction(updatedExperienceParameters.getFrench().getInstruction());
        dataSample.getFrench().setInput(updatedExperienceParameters.getFrench().getInput());
        dataSample.getFrench().setOutput(updatedExperienceParameters.getFrench().getOutput());
        dataSample.getFrench().setAdditionalInfo(updatedExperienceParameters.getFrench().getAdditionalInfo());

        try {
          dataSample.setTotalTokensEnglish(dataSampleService.getNumberTokenInText(updatedExperienceParameters.getEnglish().getOutput() + "\n\n" + updatedExperienceParameters.getEnglish().getAdditionalInfo()));
          dataSample.setTotalTokensFrench(dataSampleService.getNumberTokenInText(updatedExperienceParameters.getFrench().getOutput() + "\n\n" + updatedExperienceParameters.getFrench().getAdditionalInfo()));
        } catch (IOException e) {
          throw new RuntimeException(e);
        } catch (InterruptedException e) {
          throw new RuntimeException(e);
        }

        if (!dataSample.isProcessed() && updatedExperienceParameters.isProcessed()){
          dataSample.setProcessedDate(new Date());
        }
        dataSample.setProcessed(updatedExperienceParameters.isProcessed());
        // Updating collections like tags and pictures
        dataSample.setTags(updatedExperienceParameters.getTags());  // Assuming overwrite is okay
        dataSample.setPictures(updatedExperienceParameters.getPictures());

        dataSampleRepository.save(dataSample);
        return ResponseEntity.ok(dataSample);
      })
      .orElseGet(() -> ResponseEntity.notFound().build());
  }

  @PutMapping("/softdelete/{id}")
  public ResponseEntity<String> softDeleteDataSample(@PathVariable Long id) {
    return dataSampleRepository.findById(id)
      .map(dataSample -> {
        dataSample.setDeleted(true);
        dataSampleRepository.save(dataSample);
        return ResponseEntity.ok("The data sample has been soft deleted successfully.");
      })
      .orElseGet(() -> ResponseEntity.notFound().build());
  }

  @DeleteMapping("/{id}")
  public ResponseEntity<String> deleteDataSample(@PathVariable Long id) {
    return dataSampleRepository.findById(id)
      .map(dataSample -> {
        dataSampleRepository.delete(dataSample);
        return ResponseEntity.ok("The data sample has been deleted successfully.");
      })
      .orElseGet(() -> ResponseEntity.notFound().build());
  }

  private Sort getSortDirection(String sortBy, String sortOrder) {
    if (sortOrder.equalsIgnoreCase("asc")) {
      return Sort.by(sortBy).ascending();
    } else {
      return Sort.by(sortBy).descending();
    }
  }*/

}
