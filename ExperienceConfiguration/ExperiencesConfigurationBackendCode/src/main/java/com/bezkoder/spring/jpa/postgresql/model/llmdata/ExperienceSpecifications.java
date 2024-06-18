package com.bezkoder.spring.jpa.postgresql.model.llmdata;

import com.bezkoder.spring.jpa.postgresql.model.llmdata.dto.DataSamplesFilters;
import org.springframework.stereotype.Component;
import org.springframework.data.jpa.domain.Specification;
import jakarta.persistence.criteria.*;

import java.util.ArrayList;
import java.util.List;

@Component
public class ExperienceSpecifications {

  /*
  public static Specification<Experience> withFilters(DataSamplesFilters filters) {
    return (root, query, criteriaBuilder) -> {

      List<Predicate> predicates = new ArrayList<>();

      // Filtering by minimum quality
      if (filters.getMinQuality() != null) {
        predicates.add(criteriaBuilder.greaterThanOrEqualTo(root.get("quality"), filters.getMinQuality()));
      }

      // Filtering by maximum quality
      if (filters.getMaxQuality() != null) {
        predicates.add(criteriaBuilder.lessThanOrEqualTo(root.get("quality"), filters.getMaxQuality()));
      }

      // Filtering by minimum positivity rating
      if (filters.getMinPositivityRating() != null) {
        predicates.add(criteriaBuilder.greaterThanOrEqualTo(root.get("positivityRating"), filters.getMinPositivityRating()));
      }

      // Filtering by maximum positivity rating
      if (filters.getMaxPositivityRating() != null) {
        predicates.add(criteriaBuilder.lessThanOrEqualTo(root.get("positivityRating"), filters.getMaxPositivityRating()));
      }

      // Filtering by processed status
      if (filters.getProcessed() != null) {
        predicates.add(criteriaBuilder.equal(root.get("processed"), filters.getProcessed()));
      }

      // Filtering by processed status
      if (filters.getDeleted() != null) {
        predicates.add(criteriaBuilder.equal(root.get("deleted"), filters.getDeleted()));
      }


      // Filtering by source (handling multiple sources)
      if (filters.getSources() != null && !filters.getSources().isEmpty()) {
        CriteriaBuilder.In<Source> sourceInClause = criteriaBuilder.in(root.get("source"));
        for (String source : filters.getSources()) {
          sourceInClause.value(Source.valueOf(source));
        }
        predicates.add(sourceInClause);
      } else {
        // If the list is empty or null, add a FALSE predicate
        Predicate falsePredicate = criteriaBuilder.equal(criteriaBuilder.literal(1), 0);
        predicates.add(falsePredicate);
      }

      // Filtering by reference (handling multiple references)
      if (filters.getReferences() != null && !filters.getReferences().isEmpty()) {
        CriteriaBuilder.In<Reference> referenceInClause = criteriaBuilder.in(root.get("reference"));
        for (String reference : filters.getReferences()) {
          referenceInClause.value(Reference.valueOf(reference));
        }
        predicates.add(referenceInClause);
      } else {
        // If the list is empty or null, add a FALSE predicate
        Predicate falsePredicate = criteriaBuilder.equal(criteriaBuilder.literal(1), 0);
        predicates.add(falsePredicate);
      }



      // Filtering by tags
      if (filters.getTags() != null && !filters.getTags().isEmpty()) {
        // Create a join on the element collection
        Join<Experience, Tag> tagJoin = root.join("tags");

        // Create an IN clause for the enum type directly
        CriteriaBuilder.In<Tag> tagInClause = criteriaBuilder.in(tagJoin);
        for (String tag : filters.getTags()) {
          tagInClause.value(Tag.valueOf(tag)); // Convert string to Tag enum correctly
        }

        predicates.add(tagInClause);
      }

      query.distinct(true); // Ensure distinct results, especially useful when joining tables like tags

      return criteriaBuilder.and(predicates.toArray(new Predicate[0]));
    };
  }*/
}
