package com.marlabs.assessment.api;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public record AnswerRequest(
        @NotBlank String tenant,
        @NotBlank String role,
        @JsonProperty("as_of") @NotBlank @Pattern(regexp = "\\d{4}-\\d{2}-\\d{2}") String asOf,
        @JsonProperty("document_text") @NotBlank String documentText
) {
}
