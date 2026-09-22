package com.marlabs.assessment.api;

import jakarta.validation.Validation;
import jakarta.validation.Validator;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class AnswerRequestTest {
    private final Validator validator = Validation.buildDefaultValidatorFactory().getValidator();

    @Test
    void rejectsMissingCallerFields() {
        var violations = validator.validate(new AnswerRequest("", "", "bad", ""));

        assertFalse(violations.isEmpty());
    }

    @Test
    void acceptsValidPublicRequestShape() {
        var violations = validator.validate(new AnswerRequest("acme", "manager", "2024-08-01", "Benefit: Travel"));

        assertTrue(violations.isEmpty());
    }
}
